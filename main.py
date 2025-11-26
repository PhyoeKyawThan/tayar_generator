import requests
import os
from typing import Optional
from pydub import AudioSegment
from requests.exceptions import RequestException

def download_and_convert_to_opus(url: str, save_path: str, filename: Optional[str] = None, bitrate: Optional[str] = '64k') -> bool:
    """
    Downloads a direct audio file from a URL and converts it to the Opus format.

    Args:
        url (str): The direct URL to the audio file (e.g., .mp3, .wav).
        save_path (str): The local directory to save the files.
        filename (str, optional): The name for the final Opus file (e.g., "song.opus").
                                   Inferred from URL if None.
        bitrate (str): The desired bitrate for the Opus file (e.g., '64k', '96k').

    Returns:
        bool: True if both download AND conversion were successful, False otherwise.
    """
    if not filename:
        temp_filename = url.split('/')[-1].split('?')[0]
        if not temp_filename or '.' not in temp_filename:
            print("❌ Failure: Could not infer filename from URL.")
            return False
    else:
        temp_filename = filename.rsplit('.', 1)[0] + "_temp_dl." + filename.rsplit('.', 1)[-1]

    input_filepath = os.path.join(save_path, temp_filename)
    
    # Final output path for the Opus file
    output_filepath = os.path.join(save_path, filename if filename else temp_filename.rsplit('.', 1)[0] + ".opus")
    
    os.makedirs(save_path, exist_ok=True)

    # --- 2. DOWNLOAD ---
    try:
        print(f"Starting download from: {url}")
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()

        with open(input_filepath, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f"✅ Downloaded successfully to temporary file.")

    except RequestException as e:
        print(f"❌ Download Error: {e}")
        return False
    except Exception as e:
        print(f"❌ An unexpected error occurred during download: {e}")
        return False

    # --- 3. CONVERSION ---
    try:
        print(f"Starting conversion to Opus ({bitrate})...")
        audio = AudioSegment.from_file(input_filepath)

        audio.export(
            out_f=output_filepath,
            format="opus",
            bitrate=bitrate,
            codec="libopus"
        )
        print(f"✅ Conversion successful! Saved as: {os.path.basename(output_filepath)}")
        return True # Final success return

    except FileNotFoundError:
        print("❌ Conversion Error: FFmpeg is not installed or not found in system PATH.")
        return False
    except Exception as e:
        print(f"❌ An error occurred during conversion: {e}")
        return False
    finally:
        # Clean up the temporary downloaded file
        if os.path.exists(input_filepath):
            os.remove(input_filepath)
            print(f"🗑️ Removed temporary file: {os.path.basename(input_filepath)}")


if __name__ == "__main__":
    
    import json
    with open("data_collection.json", "r") as f:
        lists = json.loads(f.read())
    success_list = []
    for t in lists:
        if download_and_convert_to_opus(t['link'], save_path="audios", filename=t['title']):
            success_list.append({
              "title": t['title'],
              "sayartaw": t['sayartaw'],
              "description":
                  "ဗုဒ္ဓဘာသာ၏ အခြေခံသီရိဝင် အယူအဆများကို ဝင်ရိုးအဖြစ်ရှင်းလင်းပြောကြားထားသော အဆိုအထားပါသည်။",
              "audioPath":
                  f"assets/audios/{t['title']}",
              "srtPath": None,
              "imagePath": None,
              "isBookMark": False,
            })
            
    with open("dataset.json", "w") as f:
        f.write(json.dumps(success_list))
            