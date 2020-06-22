<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Карта</title>
    <style>
        html, body { 
            height: 100%; 
            width: 100%; 
            margin: 0; 
        }
        #map { 
            height: 90%; 
            width: 100%; 
        }
    </style>
    <script src="https://maps.api.2gis.ru/2.0/loader.js?pkg=full"></script>
    <script type="text/javascript">
        var map;
    
        var markers = [];
       
        

        DG.then(function () {
            map = DG.map('map', {
                center: [56.018012, 92.868991],
                zoom: 4
            });
            DG.marker([55.994433, 92.797081]) // Координаты
            .addTo(map)
            .bindPopup('В столовой остаётся лишняя еда. Помогите съесть!') // Описание предложения
            .addEventListener(
                'dblclick', 
                function(){
                    location.href = "tg://resolve?domain=notveryoriginalbot"; // Ссылка на автора предложения
                }
            );
        });
        
    </script>
</head>
<body>

    <div id="map"></div>
    <a href="tg://resolve?domain=notveryoriginalbot" target="blank"><button>Наш бот</button></a>
    <!-- <a href="tel:+79607715528" target="blank"><button>Мой номер</button></a> -->
    <!-- 
        Если пользователь с юзернеймом, то отправляем ссылку на диалог с ним
        Если пользователь с телефоном, то отправляем на звонок с ним
     -->
    <?php
        if $username != null {
            echo
        }

    ?>
</body>

</html>