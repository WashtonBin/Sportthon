# Lets import moviepy, lets also import numpy we will use it a some point
from moviepy import *
from moviepy import VideoFileClip
from read_write_json import read_from_json
import os

def generate_highlights(video_path):  
          
    # We load our video
    video = VideoFileClip(video_path)
 
    path2 = r"highlights.json" 
         
    clips = read_from_json(path2)

    highlights = []
    for c in clips:
        start = (c['start-time'])
        end = (c['end-time'])
        clip = video.subclipped(start, end)
        highlights.append(clip)
 
    scenes = concatenate_videoclips(highlights)
    scenes.write_videofile("./result/basketball_highlights.mp4", fps=24)
    
    
    
def get_clip_paths(folder_path):
    """
    Reads all file paths from a given folder.

    Args:
        folder_path (str): The path to the folder containing the clips.

    Returns:
        list: A list of file paths in the folder.
    """
    clip_paths = []
    try:
        for filename in os.listdir(folder_path):
            file_path = os.path.join(folder_path, filename)
            if os.path.isfile(file_path):  # Check if it's a file
                clip_paths.append(file_path)
    except FileNotFoundError:
        print(f"Error: Folder not found: {folder_path}")
        return []  # Return an empty list if the folder is not found
    except Exception as e:
        print(f"An error occurred: {e}")
        return []  # Return an empty list if any other error occurs
    return clip_paths

