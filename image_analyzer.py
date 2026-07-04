import cv2
import numpy as np
import os


print(">>> IMAGE ANALYZER AKTIF <<<")



def analyze_image(image_path, analyzed_folder):


    image = cv2.imread(image_path)


    if image is None:

        raise Exception(
            f"Fotoğraf okunamadı: {image_path}"
        )



    output = image.copy()



    # -------------------------
    # GRİ GÖRÜNTÜ
    # -------------------------

    gray = cv2.cvtColor(
        image,
        cv2.COLOR_BGR2GRAY
    )


    blur = cv2.GaussianBlur(
        gray,
        (5,5),
        0
    )



    edges = cv2.Canny(
        blur,
        50,
        150
    )



    kernel = np.ones(
        (3,3),
        np.uint8
    )


    edges = cv2.dilate(
        edges,
        kernel,
        iterations=1
    )



    contours,_ = cv2.findContours(
        edges,
        cv2.RETR_EXTERNAL,
        cv2.CHAIN_APPROX_SIMPLE
    )



    # -------------------------
    # HASAR ALANI
    # -------------------------

    damage_area = 0
    valid_contours = 0

    for c in contours:


        area = cv2.contourArea(c)


        if area > 150 and area < 5000:


            damage_area += area

            valid_contours += 1

            x,y,w,h = cv2.boundingRect(c)


            cv2.rectangle(
                output,
                (x,y),
                (x+w,y+h),
                (0,0,255),
                2
            )




    height,width = gray.shape


    total_area = height * width


    # -------------------------
    # KENAR YOĞUNLUĞU
    # -------------------------

    edge_pixels = cv2.countNonZero(edges)

    edge_percent = (
        edge_pixels / total_area
    ) * 100


    # -------------------------
    # GELİŞMİŞ HASAR ORANI
    # -------------------------

    crack_ratio = (
        damage_area / total_area
    ) * 100


    dark_pixels = np.sum(gray < 90)

    dark_ratio = (
        dark_pixels / total_area
    ) * 100



    # -------------------------
    # GERÇEK HASAR ORANI
    # -------------------------

    brightness = float(np.mean(gray))
    contrast = float(np.std(gray))

    contour_score = len(contours)

    crack_damage = crack_ratio * 0.8


    # karanlık boşluk (yıkım belirtisi)
    void_damage = 0

    if dark_ratio > 40:
        void_damage = dark_ratio * 0.5

    elif dark_ratio > 25:
       void_damage = dark_ratio * 0.25


    # yüzey bozukluğu
    texture_damage = edge_percent * 0.15


    damage_percent = (
        crack_damage
        +
        void_damage
        +
        texture_damage
    )


    damage_percent = round(
        min(damage_percent,100),
        2
    )



    # -------------------------
    # YENİ STABİL RİSK SKORU
    # -------------------------

    score = 0


    # 1) Hasar oranı ana faktör
    if damage_percent < 5:
        score += 5

    elif damage_percent < 15:
        score += 20

    elif damage_percent < 30:
        score += 45

    elif damage_percent < 50:
        score += 70

    else:
        score += 90



    # 2) Gerçek yapısal bozulma
    if dark_ratio > 45:
        score += 10

    elif dark_ratio > 30:
        score += 5



    # 3) Çok parçalı kırılma
    if valid_contours > 80:
        score += 10

    elif valid_contours > 40:
        score += 5


    # 4) Aşırı kenar yoğunluğu
    if edge_percent > 45:
        score += 5



    # 5) temiz yapı koruması
    if brightness > 120 and dark_ratio < 20:
        score -= 15


    score = max(score,0)
    score = min(score,100)



    print("HASAR %:", damage_percent)
    print("EDGE %:", edge_percent)
    print("KONTUR:", contour_score)
    print("HAM SKOR:", score)

    score = int(min(score,100))



    # -------------------------
    # HASAR SINIFI
    # -------------------------


    if score < 25:


        damage = "Düşük"

        structure = "Sağlam"

        scenario = "Koruyucu Bakım"



    elif score < 50:


        damage = "Orta"

        structure = "İzleme Gerekli"

        scenario = "Yerel Onarım"



    elif score < 70:


        damage = "Yüksek"

        structure = "Riskli"

        scenario = "Güçlendirme"



    else:


        damage = "Çok Yüksek"

        structure = "Kritik"

        scenario = "Restorasyon"




    # -------------------------
    # MALZEME
    # -------------------------


    if brightness > 170:

        material = "Açık Renk Taş"


    elif brightness > 110:

        material = "Taş / Tuğla"


    else:

        material = "Koyu Taş Yüzey"





    recommendation = (
        scenario +
        " önerilir."
    )




    filename = os.path.basename(
        image_path
    )



    save_path = os.path.join(
        analyzed_folder,
        filename
    )



    cv2.imwrite(
        save_path,
        output
    )




    # TERMINAL TEST

    print("====================")

    print(
        "SKOR:",
        score
    )

    print(
        "PARLAKLIK:",
        round(brightness,2)
    )

    print(
        "KONTRAST:",
        round(contrast,2)
    )

    print(
        "KONTUR:",
        contour_score
    )

    print(
        "HASAR %:",
        round(damage_percent,2)
    )

    print("====================")




    return {


        "image": filename,


        "damage": damage,


        "material": material,


        "structure": structure,


        "risk": score,


        "scenario": scenario,


        "crack_percent":
            round(damage_percent,2),


        "brightness":
            round(brightness,2),


        "contrast":
            round(contrast,2),


        "edge_density":
            round(edge_percent,2),


        "texture_score":
            contour_score,


        "recommendation":
            recommendation,


        "explanation":

            f"""
Parlaklık:
{round(brightness,2)}

Kontrast:
{round(contrast,2)}

Kontur:
{contour_score}

Hasar oranı:
%{round(damage_percent,2)}
"""

    }