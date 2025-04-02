import time

while True:
    try:
        # 
        print("Dosyalar işleniyor...")
        
        # Burada dosya işlemlerini veya diğer kodlarını yazabilirsin
        # Örneğin:
        # with open('dosya.txt', 'r') as file:
        #     veri = file.read()
        
        # Simülasyon olarak, bir hata oluşturma (gereksiz)
        # raise Exception("Bir hata oluştu!")  # Hata simülasyonu
        
        time.sleep(5)  

    except Exception as e:
        print(f"Hata oluştu: {e}. İşlem tekrar ediliyor...")
        time.sleep(2) 
