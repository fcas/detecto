import matplotlib.pyplot as plt
import os
from torchvision import transforms
from skimage import io

# Relative folder paths/names for your train/test image files and XML labels
IMAGES = 'images'


img_name = os.path.join(IMAGES, 'frame199.jpg')
image = io.imread(img_name)
print(image.shape)
plt.imshow(image)
plt.show()
from detecto.core import Model
model = Model(3)
model.predict_top(image)

# Apply some preliminary transformations to the image we read in
transform_img = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize(1800),  # Scale image height from 1080 to 216 for faster training
    transforms.RandomHorizontalFlip(0.5),  # Randomly flip some images for data augmentation
    transforms.ColorJitter(saturation=0.5),  # Randomize saturation for image augmentation
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],  # default for pre-trained models
                         std=[0.229, 0.224, 0.225]),
])

img = transform_img(image)
# Shape should be (3, height, width), where 3 is the number of colors in RGB
# This shape is necessary for when we eventually feed it into the pretrained models
print(img.shape)
print(img.min(), img.max())

from detecto.core import Dataset, DataLoader, Model
from detecto.utils import reverse_normalize, xml_to_csv
from detecto.visualize import show_labeled_image, plot_prediction_grid, detect_video

xml_to_csv('xml_labels', 'labels.csv')


dataset = Dataset('labels.csv', 'images', transform=transform_img)
image, target = dataset[0]
# Shows image shape, bounds of the box, and the label for the item in the box
print(image.shape, target['boxes'], target['labels'])

show_labeled_image(image, target['boxes'])

loader = DataLoader(dataset, batch_size=1, shuffle=True)
val_loader = DataLoader(dataset, batch_size=1, shuffle=False)

model = Model(3)
model.predict(image)
losses = model.fit(loader, val_loader, epochs=1, lr_step_size=2, verbose=True)
plt.plot(losses)
plt.show()


# Loading working model
model = Model.load('model.pth', 3)


image = dataset[1][0]
labels, boxes, scores = model.predict(image)
print(labels, boxes, scores, image.shape)
show_labeled_image(reverse_normalize(image), boxes)

test_images = [dataset[i][0] for i in range(2)]
plot_prediction_grid(model, test_images, (1, 2))

# detect_video(model, 'videos/input_short.mp4', 'videos/output_short.avi')
