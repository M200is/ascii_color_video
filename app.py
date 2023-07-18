import cv2
import pygame as pg
import numpy as np
import os
import numpy as np
from numba import njit

os.mkdir('output')
os.mkdir('img')
os.mkdir('videos')

extension = ''
name = ''
image_ex = ["jpg", "jpeg", "png"]
video_ex = ["mp4"]
wait = True


@njit(fastmath=True)
def conversion(image, gray_image, width, height, color_coeff, ascii_coeff, step):
    arr = []
    for x in range(0, width, step):
        for y in range(0, height, step):
            char_index = gray_image[x, y] // ascii_coeff
            if char_index:
                r, g, b = image[x, y] // color_coeff
                arr.append((char_index, (r, g, b), (x, y)))
    return arr


class filename:
    def __init__(self, font_size=50):
        pg.init()
        self.file_name = ''
        self.RES = [800, 600]
        self.surface = pg.display.set_mode(self.RES)
        self.text_color = [0, 0, 0]
        self.clock = pg.time.Clock()
        self.screen_color = [255, 255, 255]
        self.font = pg.font.SysFont(None, font_size, True, False)
        self.text_surface = self.font.render(
            self.file_name, True, self.text_color)

    def run(self):
        check = True
        while check:
            for event in pg.event.get():
                # print(self.file_name)
                if event.type == pg.QUIT:
                    exit()
                if event.type == pg.KEYDOWN:
                    if event.key == pg.K_RETURN:
                        extension = self.file_name.split('.', 1)[1]
                        check = False
                    elif event.key == pg.K_BACKSPACE:
                        self.file_name = self.file_name[:-1]
                    else:
                        self.file_name += event.unicode
                    self.text_surface = self.font.render(
                        self.file_name, True, self.text_color)
            self.surface.fill(self.screen_color)
            text_Rect = self.text_surface.get_rect()
            text_Rect.centerx = round(400)
            text_Rect.y = 300
            self.surface.blit(self.text_surface, text_Rect)
            pg.display.flip()
        name = self.file_name
        return name, extension


class Converter:
    def __init__(self, font_size=12, color_lvl=8):
        pg.init()
        self.path = name
        self.capture = cv2.VideoCapture(name)
        self.COLOR_LVL = color_lvl
        self.image, self.gray_image = self.get_image()  # 컬러, 흑백 이미지 불러오기
        # 가로세로
        self.RES = self.WIDTH, self.HEIGHT = self.image.shape[0], self.image.shape[1]
        self.surface = pg.display.set_mode(self.RES)
        self.clock = pg.time.Clock()

        self.ASCII_CHARS = '.",:;!~+-xmo*#W&*@'  # 사용할 아스키
        self.ASCII_COEFF = 255 // (len(self.ASCII_CHARS)-1)  # 14

        self.font = pg.font.SysFont('Courier New', font_size, bold=True)  # 폰트
        self.CHAR_STEP = int(font_size * 0.6)  # 스텝값, 조절 가능
        self.PALETTE, self.COLOR_COEFF = self.create_palette()  # 색상 정보들 받아옴

        self.rec_fps = self.capture.get(cv2.CAP_PROP_FPS)  # 영상 프레임
        self.recode = False
        self.recorder = cv2.VideoWriter(
            'output/ascii_col.mp4', cv2.VideoWriter_fourcc(*'mp4v'), self.rec_fps, self.RES)  # 녹화

    def draw_ascii_image(self):
        image, gray_image = self.get_image()
        arr = conversion(image, gray_image, self.WIDTH, self.HEIGHT,
                         self.COLOR_COEFF, self.ASCII_COEFF, self.CHAR_STEP)
        for char_index, color, pos in arr:
            char = self.ASCII_CHARS[char_index]
            self.surface.blit(self.PALETTE[char][color], pos)

    def create_palette(self):  # 팔레트설정
        # 0~255까지 컬레 레벨만큼의 배열 생성, 간격을 coeff에 저장
        colors, color_coeff = np.linspace(
            0, 255, num=self.COLOR_LVL, dtype=int, retstep=True)
        color_palette = [np.array(
            [r, g, b]) for r in colors for g in colors for b in colors]  # rgb로 팔레트 생성
        palette = dict.fromkeys(self.ASCII_CHARS, None)
        for char in palette:
            char_palette = {}
            for color in color_palette:
                color_key = tuple(color // color_coeff)
                char_palette[color_key] = self.font.render(
                    char, False, tuple(color))
            palette[char] = char_palette
        return palette, color_coeff

    def get_image(self):  # 이미지 가져오기
        if extension in image_ex:
            self.cv2_image = cv2.imread(self.path)
        elif extension in video_ex:
            ret, self.cv2_image = self.capture.read()  # 프레임 읽기
            if not ret:  # 영상 끝나면 나가기
                print(extension)
                exit()
        else:
            exit()
        transposed_image = cv2.transpose(
            self.cv2_image)  # 비율 조정용 transpose 이미지
        image = cv2.cvtColor(transposed_image, cv2.COLOR_BGR2RGB)  # 컬러 이미지 저장
        gray_image = cv2.cvtColor(
            transposed_image, cv2.COLOR_BGR2GRAY)  # 흑백 이미지 저장
        return image, gray_image

    def draw_cv2_image(self):  # cv2창 출력(선택)
        resized_cv2_image = cv2.resize(
            self.cv2_image, (540, 360), interpolation=cv2.INTER_AREA)  # 사이즈 540*360조정
        cv2.imshow('img', resized_cv2_image)  # 이미지 cv2창 출력
        cv2.waitKey(10)

    def draw(self):
        self.surface.fill('black')  # 배경 검은색
        self.draw_ascii_image()  # 아스키 출력
        self.draw_cv2_image()  # cv2창

    def save_image(self):
        pygame_imgae = pg.surfarray.array3d(self.surface)
        cv2_img = cv2.transpose(pygame_imgae)
        cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_RGB2BGR)
        cv2.imwrite('./output/img/converted_image.jpg', cv2_img)

    def run(self):
        while (True):
            for i in pg.event.get():
                if i.type == pg.QUIT:
                    exit()
                elif i.type == pg.KEYDOWN:
                    if i.key == pg.K_s:
                        self.save_image()
            self.draw()
            pg.display.set_caption(str(self.clock.get_fps()))
            pg.display.flip()
            self.clock.tick()


if __name__ == '__main__':
    app1 = filename()
    name, extension = app1.run()
    app2 = Converter()
    app2.run()
