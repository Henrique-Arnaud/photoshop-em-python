from asyncio import events
from email.mime import image
import io
import os
from tkinter import Scrollbar
from unicodedata import mirrored
import PySimpleGUI as sg
from PIL import Image
import requests
from pathlib import Path
from PIL.ExifTags import TAGS, GPSTAGS
import webbrowser
from PIL import ImageFilter
import tempfile
from PIL import ImageEnhance
import shutil

file_types = [
    ("JPEG (*.jpg)", "*.jpg"),
    ("PNG (*.png)", "*.png"),
    ("Todos os arquivos (*.*)", "*.*")
]


fields = {
    "File name" : "File name",
    "File size" : "File size",
    "Model" : "Camera Model",
    "ExifImageWidth" : "Width",
    "ExifImageHeight" : "Height",
    "DateTime" : "Creating Date",
    "static_line" : "*",
    "MaxApertureValue" : "Aperture",
    "ExposureTime" : "Exposure",
    "FNumber" : "F-Stop",
    "Flash" : "Flash",
    "FocalLength" : "Focal Length",
    "ISOSpeedRatings" : "ISO",
    "ShutterSpeedValue" : "Shutter Speed",
    "GPSLatitude": "Latitude",
    "GPSLongitude": "Longitude"
}


menu_def = [
    ['Arquivo de Imagem', ['Abrir Imagem','Thumbnail', 'Qualidade Reduzida', 'Escolher Formato', ['PNG', 'JPEG'], 'Salvar Imagem']],
    ['Imagem URL', ['Abrir Imagem URL']],
    ['Filtro', ['Cinza', 'Muda 4 Cores', 'Sepia', 'Blur', 'Box Blur','Contour', 'Detail', 'Edge enhance', 'Emboss', 'Find edges', 'Smooth', 'Sharpen','Gaussian blur']],
    ['Info Imagem', ['Dados da Imagem', 'Pesquisar Localização']],
    ['Movimentação Imagem',['Espelhar', ['Left->Right', 'Top->Bottom', 'Transpose'], 'Redimensionar', 'Rotacionar', ['90°', '-90°'], 'Recortar']]
]

def AbrirImg(imagem, window):
    img = Image.open(imagem)
    bio = io.BytesIO()
    img.save(bio, format = "PNG")
    window["-IMAGE-"].erase()
    window["-IMAGE-"].draw_image(data = bio.getvalue(), location = (0,0))

def Thumb(input_file, output_file):
    imagem = Image.open(input_file)
    imagem.save(output_file)
    imagem.thumbnail((75,75))
    imagem.save("Thumbnail.jpg")

def QualRed(input_file, output_file):
    imagem = Image.open(input_file)
    imagem.save(output_file, quality = 1)

def TamOriginal_Form(input_file, output_file, formato):
    imagem = Image.open(input_file)
    imagem.save(output_file, format=formato)

def muda_para_cinza(input_file, output_file):
    imagem = Image.open(input_file)
    imagem = imagem.convert("1", dither=1)
    imagem.save(output_file)

def muda_4cores(imagem_entrada, imagem_saida):
    imagem = Image.open(imagem_entrada)
    imagem = imagem.convert("P", palette=Image.Palette.ADAPTIVE, colors=4)
    imagem.save(imagem_saida)

def calcula_paleta(branco):
    paleta = []
    r, g, b = branco
    for i in range(255):
        new_red = r * i // 255
        new_green = g * i // 255
        new_blue = b * i // 255
        paleta.extend((new_red, new_green, new_blue))
    return paleta

def converte_sepia(input, output):
    branco = (200, 1, 100)
    paleta = calcula_paleta(branco)
    imagem = Image.open(input)
    imagem = imagem.convert("L")
    imagem.putpalette(paleta)
    sepia = imagem.convert("RGB")
    sepia.save(output)

def image_format(input_file):
    imagem = Image.open(input_file)
    print(f"Formato: {imagem.format_description}")


def get_exif_data(path):
    exif_data = {}
    try:
        image = Image.open(path)
        info = image._getexif()
    except OSError:
        info = {}

    #Se não encontrar o arquivo
    if info is None:
        info = {}
    for tag, value in info.items():
        decoded = TAGS.get(tag, tag)
        if decoded == "GPSInfo":
            gps_data = {}
            for gps_tag in value:
                sub_decoded = GPSTAGS.get(gps_tag, gps_tag)
                gps_data[sub_decoded] = value[gps_tag]
            exif_data[decoded] = gps_data
        else:
            exif_data[decoded] = value

    return exif_data

def infoImg(imagem, window):
    image_path = Path(imagem)
    exif_data = get_exif_data(image_path.absolute())
    for field in fields:
        if field == "File name":
            window[field].update(image_path.name)
        elif field == "File size":
            window[field].update(image_path.stat().st_size)
        elif "GPS" in field:
            if(field == "GPSLatitude"):
                latitude = decimal_coords(exif_data.get("GPSInfo").get(field, "Sem Info"), exif_data.get("GPSInfo").get("GPSLatitudeRef", "N"))
                window[field].update(latitude)
            elif(field == "GPSLongitude"):
                longitude = decimal_coords(exif_data.get("GPSInfo").get(field, "Sem Info"), exif_data.get("GPSInfo").get("GPSLongitudeRef", "W"))
                window[field].update(longitude)
        else:
            window[field].update(exif_data.get(field, "Sem Info"))
    return latitude, longitude

def decimal_coords(coords, ref):
    decimal_degrees = float(coords[0]) + float(coords[1]) / 60 + float(coords[2]) / 3600
    if ref == "S" or ref == "W":
        decimal_degrees = -decimal_degrees
    return decimal_degrees

def filter(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.BLUR)
    filtered_image.save(output_image)

def boxBlur(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.BoxBlur(radius=3))
    filtered_image.save(output_image)

def contour(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.CONTOUR)
    filtered_image.save(output_image)

def detail(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.DETAIL)
    filtered_image.save(output_image)

def edge_enhance(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.EDGE_ENHANCE)
    filtered_image.save(output_image)

def emboss(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.EMBOSS)
    filtered_image.save(output_image)

def find_edges(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.FIND_EDGES)
    filtered_image.save(output_image)

def gaussian(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.GaussianBlur)
    filtered_image.save(output_image)

def sharpen(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.SHARPEN)
    filtered_image.save(output_image)

def smooth(input_image, output_image):
    image = Image.open(input_image)
    filtered_image = image.filter(ImageFilter.SMOOTH)
    filtered_image.save(output_image)

def mirrorLR(image_path, output_image_path):
    image = Image.open(image_path)
    mirror_image = image.transpose(Image.FLIP_LEFT_RIGHT) #FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, TRANSPOSE
    mirror_image.save(output_image_path)

def mirrorTB(image_path, output_image_path):
    image = Image.open(image_path)
    mirror_image = image.transpose(Image.FLIP_TOP_BOTTOM) #FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, TRANSPOSE
    mirror_image.save(output_image_path)

def mirrorTranspose(image_path, output_image_path):
    image = Image.open(image_path)
    mirror_image = image.transpose(Image.TRANSPOSE) #FLIP_LEFT_RIGHT, FLIP_TOP_BOTTOM, TRANSPOSE
    mirror_image.save(output_image_path)

def resize(input_image_path, output_image_path, size):
    image = Image.open(input_image_path)
    resized_image = image.resize(size)
    resized_image.save(output_image_path)

def rotate(image_path, degrees_to_rotate, output_image_path):
    image_obj = Image.open(image_path)
    rotated_image = image_obj.rotate(degrees_to_rotate)
    rotated_image.save(output_image_path)

def crop_image(image_path, coords, output_image_path):
    image = Image.open(image_path)
    cropped_image = image.crop(coords)
    cropped_image.save(output_image_path)

def brilho(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Brightness(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def contraste(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Contrast(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def cores(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Color(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

def nitidez(filename, fator, output_filename):
    image = Image.open(filename)
    enhancer = ImageEnhance.Sharpness(image)
    new_image = enhancer.enhance(fator)
    new_image.save(output_filename)

efeitos = {
    "Normal": shutil.copy,
    "Brilho": brilho,
    "Cores": cores,
    "Contraste": contraste,
    "Nitidez": nitidez
}

def aplica_efeito(values, window, imagem):
    efeito_selecionado = values["-EFEITOS-"]
    filename = imagem
    factor = values["-FATOR-"]
    
    if filename:
        if efeito_selecionado == "Normal":
            efeitos[efeito_selecionado](filename, tmp_file)
        else:
            efeitos[efeito_selecionado](filename, factor, tmp_file)
        
        image = Image.open(tmp_file)
        image.thumbnail((400, 400))
        bio = io.BytesIO()
        image.save(bio, format="PNG")
        window["-IMAGE-"].draw_image(data=bio.getvalue(), location=(0, 400))

def save_image(filename):
    save_filename = sg.popup_get_file("Salvar", file_types=file_types, save_as=True, no_window=True)
    if save_filename == filename:
        sg.popup_error("Você não pode substituir a imagem original!")
    else:
        if save_filename:
            shutil.copy(tmp_file, save_filename)
            sg.popup(f"Arquivo {save_filename}, salvo com sucesso!")

def info_window(imagem):
    layout = []
    for field in fields:
        layout += [[sg.Text(fields[field], size=(20,1)),
                    sg.Text("", size=(25,1), key=field)]]
    window = sg.Window("Image info", layout=layout)

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        infoImg(imagem, window)
        


tmp_file = tempfile.NamedTemporaryFile(suffix=".jpg").name

def main():
    effect_names = list(efeitos.keys())

    layout = [
        [
            sg.Graph(key="-IMAGE-", background_color= "#64778d", canvas_size=(400,400), graph_bottom_left=(0, 0), graph_top_right=(400, 400), change_submits=True, drag_submits=True),
            sg.Menu(menu_def, tearoff=False, pad=(200, 1))
        ],
        [
            sg.Text("Efeito"),
            sg.Combo(effect_names, default_value="Normal", key="-EFEITOS-", enable_events=True, readonly=True),
            sg.Slider(range=(0, 5), default_value=2, resolution=0.1, orientation="h", enable_events=True, key="-FATOR-"),
        ]
    ]

    window = sg.Window("Photoshop Python", layout=layout)

    dragging = False
    ponto_inicial = ponto_final = retangulo = None

    latitude = ()
    longitude = ()

    while True:
        event, values = window.read()
        if event == "Exit" or event == sg.WIN_CLOSED:
            break
        if event == "Abrir Imagem":
            imagem = sg.popup_get_file("Selecione arquivo")
            AbrirImg(imagem, window)
        if event == "Thumbnail":
            Thumb(imagem, "Thumbnail.jpg")
        if event == "Qualidade Reduzida":
            QualRed(imagem, "QualidadeReduzida.jpg")
        if event == "PNG":
            TamOriginal_Form(imagem, "FormatoEscolhido.png", "PNG")
        if event == "JPEG":
            TamOriginal_Form(imagem, "FormatoEscolhido.jpg", "JPEG")
        if event == "Abrir Imagem URL":
            urlLink = sg.popup_get_text("Link Imagem URL")
            url = requests.get(urlLink, stream = True).raw
            AbrirImg(url, window)
        if event == "Cinza":
            muda_para_cinza(imagem, "Cinza.jpg")
        if event == "Muda 4 Cores":
            muda_4cores(imagem, "4Cores.png")
        if event == "Sepia":
            converte_sepia(imagem, "Sepia.png")
        if event == "Dados da Imagem":
            info_window(imagem)
        if event == "Pesquisar Localização":
            latitude, longitude = infoImg(imagem, window)
            print("https://www.google.com.br/maps/search/"+str(latitude)+",+"+str(longitude)+"+/")
            webbrowser.open("https://www.google.com.br/maps/search/"+str(latitude)+",+"+str(longitude)+"+/")
        if event == 'Blur':
            filter(imagem, "blur.png")
        if event == 'Box blur':
            boxBlur(imagem, "boxblur.png")
        if event == 'Contour':
            contour(imagem, "contour.png")
        if event == 'Detail':
            detail(imagem, "detail.png")
        if event == 'Edge enhance':
            edge_enhance(imagem, "edgeenhance.png")
        if event == 'Emboss':
            emboss(imagem, "emboss.png")
        if event == 'Find edges':
            find_edges(imagem, "findedges.png")
        if event == 'Gaussian  blur':
            gaussian(imagem, "gaussianblur.png")
        if event == 'Sharpen':
            sharpen(imagem, "sharpen.png")
        if event == 'Smooth':
            smooth(imagem, "smooth.png")
        if event == 'Left->Right':
            mirrorLR(imagem, "Left_Right.jpg")
        if event == 'Top->Bottom':
            mirrorTB(imagem, "Top_Bottom.jpg")
        if event == "Transpose":
            mirrorTranspose(imagem, "Transpose.jpg")
        if event == "Redimensionar":
            altura = sg.popup_get_text("Altura da Imagem Redimensionada")
            largura = sg.popup_get_text("Largura da Imagem Redimensionada")
            resize(imagem, "ImgRedimensionada.jpg", (int(altura), int(largura)))
        if event == "90°":
            rotate(imagem, 90, "ImgRot90p.jpg")
        if event == "-90°":
            rotate(imagem, -90, "ImgRot90n.jpg")

        #utilizado para a funcao de recorte
        if event == "-IMAGE-":
            x, y = values["-IMAGE-"]
            if not dragging:
                ponto_inicial = (x, y)
                dragging = True
            else:
                ponto_final = (x, y)
            if retangulo:
                window["-IMAGE-"].delete_figure(retangulo)
            if None not in (ponto_inicial, ponto_final):
                retangulo = window["-IMAGE-"].draw_rectangle(ponto_inicial, ponto_final, line_color='red')

        elif event.endswith('+UP'):
            dragging = False
        
        if event == "Recortar":
            left = min(ponto_inicial[0], ponto_final[0])
            upper = min(400-ponto_inicial[1], 400-ponto_final[1])
            right = max(ponto_inicial[0], ponto_final[0])
            lower = max(400-ponto_inicial[1], 400-ponto_final[1])
            crop_image(imagem, (left, upper, right, lower), "ImgRecortada.jpg")

        if event in ["Abrir Imagem", "-EFEITOS-", "-FATOR-"]:
            aplica_efeito(values, window, imagem)
        if event == "Salvar Imagem" and imagem:
            save_image(imagem)

  

    
    window.close()
    
if __name__ == "__main__":
    main()


#image_format("download.jpg")

