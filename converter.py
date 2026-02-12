import ffmpeg
from wand.image import Image
import shutil
import os
import re

file_regex = re.compile(r'.*\.(png|jpg|jpeg|mp4|mpeg|wmv|mov|mkv|avi|webm|webp|gif)$')

input_folder = os.path.expanduser(r"~\Downloads\converting folder")
output_folder = os.path.expanduser(r"~\Downloads\converting folder\gifs_output")
temp_folder = os.path.expanduser(r"~\Downloads\converting folder\temp_stufff")

for file in os.listdir(input_folder):
    print(f"Attempting to convert {file}")
    re.findall
    ext_match = re.match(file_regex,file)
    if ext_match == None:
        print(file, "doesn't have a valid extension!")
        continue
    input_file = os.path.join(input_folder, file)
    #print(input_file)
    ext_name = ext_match.group(1)
    if ext_name in {"png","jpg","jpeg"}:
        filetype = "image"
    elif ext_name in {"mp4","mpeg","wmv","mov","mkv","avi","webm"}:
        filetype = "video"
    elif ext_name == "webp":
        filetype = "webp"
    elif ext_name == "gif":
        filetype = "gif"
    else:
        print("some fuckery is going on")
        continue

    if filetype == "webp":
        with Image(filename=input_file) as img: # have to use iamgemagik cause ffmpeg is obsessed and doesnt want to add anim webp https://trac.ffmpeg.org/ticket/4907 
            frame_count = len(img.sequence)
            
            if frame_count > 1:
                print(f"Detected webp as video with {frame_count} frames")

                img.coalesce() # make the gif have the full image data
                
                if os.path.exists(temp_folder):
                    shutil.rmtree(temp_folder) # delete and recreate temp folder
                
                os.makedirs(temp_folder)

                img.save(filename=os.path.join(temp_folder, "frame-%03d.png")) # save all the images to a temp folder
                
                input_file = os.path.join(temp_folder, "frame-%03d.png") # set the input for ffmpeg
            else:
                print("Webp is just a image")
                filetype = "image"

    if filetype == "image":
        stream = ffmpeg.input(input_file, loop=1, t=3) # for images with the 3 second loop
        stream = stream.filter('fps', fps=15)
    elif filetype == "video":
        stream = ffmpeg.input(input_file) # for videos
        stream = stream.filter('fps', fps=15)
    elif filetype == "webp": # this is specificaly webp animated. static webps are under images
        stream = ffmpeg.input(input_file, framerate='15')

    stream = stream.filter('format', 'rgba') # so the background has transparency
    stream = stream.filter('scale', 720, -2, flags='lanczos') # a bit big but wtvr
    
    split = stream.split() # split stream
    
    palette = split[0].filter('palettegen') # specifing that we are creating a palette
    
    out = ffmpeg.filter([split[1], palette], 'paletteuse') # use palette to create image
    
    out = out.output(os.path.join(output_folder, file+".gif")) # output folder
    
    out.run(overwrite_output=True) # run it

# just to make sure were clean at the end
if os.path.exists(temp_folder):
    shutil.rmtree(temp_folder) # delete and recreate temp folder

os.makedirs(temp_folder)