#Importation packages
import imageio.v3 as iio

### IMPORTATION IMAGES
filenames = [f"panel{i}.png" for i in range(1,9) ]
print(filenames)

gif=[]
for image in filenames:
    gif.append(iio.imread(image))
    
iio.imwrite("shadow_dynamic.gif",gif,duration=100,loop=0)
    

    