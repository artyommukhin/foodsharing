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
        DG.then(function () {
            map = DG.map('map', {
                center: [56.018012, 92.868991],
                zoom: 14
            });

<?php
        $db_name = "";
		$db = new SQLite3($db_name);

		$offers = $db->query('SELECT * FROM offers');

		while ($row = $offers->fetchArray()) {
			
			if ($row['is_complete'] == 1){
				
				$lat = $row['marker_latitude'];
				$long = $row['marker_longitude'];
				$name = $row['name'];
				$description = $row['description'];
				$user_id = $row['user_id'];
				
				$user_row = $db->querySingle('SELECT * FROM users WHERE id='.$user_id.'', true);
				$username = $user_row['name'];
				$phone = $user_row['phone'];
				
				echo "DG.marker([".$lat.",".$long."]) // Координаты
					 .addTo(map)
					 .bindPopup('".$name.":".$description."') // Описание предложения
					 .addEventListener(
						'dblclick', 
						function(){";
					if (is_null($username)){
						echo "location.href = 'tel:".$phone."'; // Ссылка на автора предложения
						}";
					}else{
						echo "location.href = 'tg://resolve?domain=".$username."'; // Ссылка на автора предложения
						}";
					}
					echo ");";
			}
		}

?>
        });
        
    </script>
</head>
<body>
    <div id="map"></div>
    <a href="tg://resolve?domain=notveryoriginalbot" target="blank"><button>Наш бот</button></a>
</body>

</html>