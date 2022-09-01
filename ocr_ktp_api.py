import sys
import kyc_config as cfg
import ocr_text_extractor as ocr
import ktp_ocr_engine as KOE
from flask import Flask
import urllib.request
from pyjarowinkler.distance import get_jaro_distance
from datetime import datetime
import os 
from google_drive_downloader import GoogleDriveDownloader as gdd
from PIL import Image


app = Flask(__name__)


@app.route('/OCR/<imgurl>/<name_partner>', methods=['GET'])
def hello_world(imgurl, name_partner):
    
    if len(imgurl) > 20:
      # gdd.download_file_from_google_drive(file_id=imgurl,
      #                               dest_path='./' + imgurl + '.jpg',
      #                               unzip=False)

      # im1 = Image.open(imgurl + '.jpg')
      # im1.save('./' + imgurl + '.png')

      # img_path = imgurl + '.png'
      return ['','','','','']

    else:
      full_url = 'https://public-tools.s3.ap-southeast-1.amazonaws.com/' + imgurl + '.png'
      urllib.request.urlretrieve(full_url, full_url.split('/')[-1])
      img_path = full_url.split('/')[-1]

    print('OCR processing '+img_path)
    ocr.process_ocr(img_path)

    hasil_final = []

    img_name = img_path.split('/')[-1].split('.')[0]
    ocr_path = cfg.json_loc+'ocr_'+img_name+'.npy'
    print('Extracting data from '+ocr_path)
    hasil = KOE.process_extract_entities(ocr_path)
    print(hasil)
    
    hasil_final.append(hasil)
 
    hasil_final.append(imgurl)
    
    hasil_final.append(hasil['identity_number'])

    if any(x in str(hasil['fullname']) for x in ['ISLAM', 'HINDU', 'KRISTEN']):
      hasil_final.append([])
    else:
      hasil_final.append(hasil['fullname'].strip())
    

    try:
      hasil_final.append(hasil['birth_date'].strftime('%Y-%m-%d'))
    except:
      hasil_final.append([])


    try:
      hasil_final.append(get_jaro_distance(hasil['fullname'].strip(), name_partner.strip()))
    except:
      hasil_final.append([])


    remove_files()
    return hasil_final


def remove_files():
  png_files = os.getcwd()
  for item in os.listdir(png_files):
      # print(item)
      try:
          if item.endswith('.png'):
              # os.remove(os.path.join(dir_name, item))
              os.remove(item)
      except:
          print('ga iso')

      try:
          if item.endswith('.jpg'):
              # os.remove(os.path.join(dir_name, item))
              os.remove(item)
      except:
          print('ga iso')


  npy_files = os.getcwd() + '/OCR_texts'
  for item in os.listdir(npy_files):
      try:
          if item.endswith('.npy'):
              # print(item)
              # os.remove(os.path.join(dir_name, item))
              os.remove(os.path.join(npy_files, item))
      except:
          print('ga iso')
          
# These two lines should always be at the end of your app.py file.
if __name__ == '__main__':
  app.run(host='0.0.0.0', port=3245, debug=True)

