from fastapi import FastAPI, Depends,UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from transformers import WhisperProcessor, WhisperForConditionalGeneration
import uvicorn
import argparse
import uuid
import os
import subprocess
import glob
import librosa
from schemas import ResponseMakeVideo

origins = ["*"]





class APIServer:
    def __init__(self,host:str,port:int,model:str,device:str) -> None:
        model_checkpoint = model
        processor_directory = model
        self.device = device
        self.model = WhisperForConditionalGeneration.from_pretrained(model_checkpoint)
        self.model.to(self.device)
        self.processor = WhisperProcessor.from_pretrained(processor_directory)
        self.model.config.forced_decoder_ids = None
        self.host = host
        self.port = port 
        self.api = FastAPI(title="Wolof Subtitles Generator Api")
        self.api.add_middleware(
            CORSMiddleware,
            allow_origins=origins,
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        self.api.mount("/static", StaticFiles(directory="static"), name="static")
        self.api.add_api_route("/makevideo",self.make_video,methods=['POST'],response_model=ResponseMakeVideo)

    async def make_video(self,upload_file:UploadFile = File(...)):
        binary_data = await upload_file.read()
        file_name = upload_file.filename
        uuid_str = str(uuid.uuid4())
        dir_path = f'./static/audio/{uuid_str}'
        os.mkdir(dir_path)
        path = f'./static/audio/{uuid_str}{file_name}'
        with open(path,"wb") as fp :
            fp.write(binary_data)
        result = self.processing(path,output_dir=dir_path)
        return ResponseMakeVideo(srt=result[0],text=result[1],video_path=result[2])

    def format_time(self,total_seconds):
        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)
        milliseconds = int((total_seconds * 1000) % 1000)
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"

    def get_audio_duration(self,file_path:str):
        cmd = 'ffprobe -i {} -show_entries format=duration -v quiet -of csv="p=0"'.format(file_path)
        output = subprocess.check_output(cmd, shell=True)
        return float(output)

    def split_audio(self,file_path, output_folder, split_interval):
        total_duration = self.get_audio_duration(file_path)
        num_segments = int(total_duration // split_interval)
        if total_duration % split_interval > 0:
            num_segments += 1
        for i in range(num_segments):
            start_time = i * split_interval
            output_file = os.path.join(output_folder, f"file{i}.wav")
            cmd = 'ffmpeg -i {} -ss {} -t {} -acodec copy {}'.format(file_path, start_time, split_interval, output_file)
            subprocess.call(cmd, shell=True)
        return total_duration

    def processing(self,audio_file_path:str,output_dir:str) -> tuple:
        split_interval_seconds = 10
        total_duration = self.split_audio(audio_file_path, output_dir, split_interval_seconds)
        all_sample = glob.glob(f'{output_dir}/*')
        all_sample_sorted = sorted(all_sample, key=os.path.getmtime)
        srt = ""
        text = ""
        last_time = 0.0
        i = 1
        for audio in all_sample_sorted:
            array, sr = librosa.load(audio, sr=16000) 
            duration = len(array) / sr
            input_features = self.processor(array, sampling_rate=16000, return_tensors="pt").input_features 
            predicted_ids = self.model.generate(input_features.to('cpu'))
            transcription = self.processor.batch_decode(predicted_ids, skip_special_tokens=True)
            text += (transcription[0]+"\n") 
            srt += f"{i}\n{self.format_time(last_time)} --> {self.format_time(last_time + duration)}\n{transcription[0]}\n\n"
            last_time += duration
            i += 1
        prefix = str(uuid.uuid4())
        with open(f'.cache/{prefix}subtitles.srt', 'w') as f:
            f.write(srt)
        cmd = f"ffmpeg -t {total_duration} -s 640x480 -f rawvideo -pix_fmt rgb24 -r 25 -i /dev/zero .cache/{prefix}video.mp4"
        subprocess.call(cmd, shell=True)
        cmd = f"ffmpeg -i .cache/{prefix}video.mp4 -i {audio_file_path} -c:v copy -c:a aac -strict experimental .cache/{prefix}output.mp4"
        subprocess.call(cmd, shell=True)
        cmd = f'ffmpeg -i ./.cache/{prefix}output.mp4 -vf "subtitles=.cache/{prefix}subtitles.srt" static/video/{prefix}-video.mp4'
        subprocess.call(cmd, shell=True)
        static_video_path = f"http://{self.host}:{self.port}/static/video/{prefix}-video.mp4"
        return (srt,text,static_video_path)
        
    def start_server(self):
        server_config = uvicorn.Config(self.api,host=self.host,port=self.port)
        server = uvicorn.Server(server_config)
        server.run()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Ceci est un server fastapi')
    parser.add_argument('--host',type=str,help="Hostname",default="0.0.0.0")
    parser.add_argument('--port',type=int,help="listenning port",default=8080)
    parser.add_argument('--model',type=str,help="the path to the model",default="./whisper-wolof")
    parser.add_argument('--device',type=str,help="CPU or GPU device",default="cpu")
    args = parser.parse_args()
    api = APIServer(host=args.host,port=args.port,model=args.model,device=args.device)
    api.start_server()