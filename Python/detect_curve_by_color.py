import os
import cv2
import numpy as np
import json

def pixel_to_data_point(x_pixel, y_pixel, x_ref, y_ref):
    data_x1, data_x2 = x_ref[0, :]
    ref_x1, ref_x2 = x_ref[1, :]
    data_y1, data_y2 = y_ref[0, :]
    ref_y1, ref_y2 = y_ref[1, :]
    delta_x_ref = abs(ref_x1 - ref_x2)
    delta_y_ref = abs(ref_y1 - ref_y2)
    delta_x_data = abs(data_x1 - data_x2)
    delta_y_data = abs(data_y1 - data_y2)
    step_x = delta_x_ref / (delta_x_data * 10000)
    step_y = delta_y_ref / 10000
    dx = abs(ref_x1 - x_pixel)
    sx = dx / step_x
    data_x_calc = data_x1 + sx * 0.0001
    dy = abs(ref_y1 - y_pixel)
    sy = dy / step_y
    data_y_calc = data_y1 + sy * 0.0001
    return data_x_calc, data_y_calc

def find_lower_contour(edge_coordinates):
    # Determine lower contour
    min_x = np.min(edge_coordinates[:, 1])
    max_x = np.max(edge_coordinates[:, 1])
    filtered_coordinates = []
    for x in range(min_x, max_x):
        # Filter edge pixels for the current x-coordinate
        filtered_edge_pixels = edge_coordinates[edge_coordinates[:, 1] == x]
        if len(filtered_edge_pixels) > 0:
            # Find the maximum y-coordinate for the current x-coordinate
            max_y = np.max(filtered_edge_pixels[:, 0])
            filtered_coordinates.append((x, max_y))
    return filtered_coordinates

def main():
    with open('config.json') as config_file:
        data = json.load(config_file)
    img_path = data['img_path']
    lower_hsv_hue = data['lower_hsv_hue']
    lower_hsv_saturation = data['lower_hsv_saturation']
    lower_hsv_value = data['lower_hsv_value']
    upper_hsv_hue = data['upper_hsv_hue']
    upper_hsv_saturation = data['upper_hsv_saturation']
    upper_hsv_value = data['upper_hsv_value']
    x1_data_value = data['x1_data_value']
    x2_data_value = data['x2_data_value']
    x1_img_pixel_value = data['x1_img_pixel_value']
    x2_img_pixel_value = data['x2_img_pixel_value']
    y1_data_value = data['y1_data_value']
    y2_data_value = data['y2_data_value']
    y1_img_pixel_value = data['y1_img_pixel_value']
    y2_img_pixel_value = data['y2_img_pixel_value']

    print(f'config parameter img_path: {img_path}')
    print(f'config parameter lower_hsv_hue: {lower_hsv_hue}')
    print(f'config parameter lower_hsv_saturation: {lower_hsv_saturation}')
    print(f'config parameter lower_hsv_value: {lower_hsv_value}')
    print(f'config parameter upper_hsv_hue: {upper_hsv_hue}')
    print(f'config parameter upper_hsv_saturation: {upper_hsv_saturation}')
    print(f'config parameter upper_hsv_value: {upper_hsv_value}')
    print(f'config parameter x1_data_value: {x1_data_value}')
    print(f'config parameter x2_data_value: {x2_data_value}')
    print(f'config parameter x1_img_pixel_value: {x1_img_pixel_value}')
    print(f'config parameter x2_img_pixel_value: {x2_img_pixel_value}')
    print(f'config parameter y1_data_value: {y1_data_value}')
    print(f'config parameter y2_data_value: {y2_data_value}')
    print(f'config parameter y1_img_pixel_value: {y1_img_pixel_value}')
    print(f'config parameter y2_img_pixel_value: {y2_img_pixel_value}')

    x_ref = np.array([[x1_data_value, x2_data_value], [x1_img_pixel_value, x2_img_pixel_value]])
    y_ref = np.array([[y1_data_value, y1_data_value], [y1_img_pixel_value, y2_img_pixel_value]])

    img_file_name = os.path.splitext(os.path.basename(img_path))[0]

    # Load the image.
    img_original = cv2.imread(img_path)
    img = img_original.copy()
    print("Loaded image.")
    lower_bound = np.array([lower_hsv_hue, lower_hsv_saturation, lower_hsv_value])
    upper_bound = np.array([upper_hsv_hue, upper_hsv_saturation, upper_hsv_value])
    hsv_image = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv_image, lower_bound, upper_bound)
    print("Selected curve.")
    # Find connected components.
    nb_components, output, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=4)
    # Find the label of the largest component (excluding background).
    max_label = np.argmax(stats[1:, -1]) + 1
    # Create an image with only the largest component.
    largest_component_mask = (output == max_label).astype(np.uint8) * 255
    cv2.imwrite(img_file_name+'_largest_component.png', largest_component_mask)
    print("Identified largest component.")
    # Find edges.
    gray = cv2.cvtColor(largest_component_mask, cv2.COLOR_GRAY2BGR)
    edges = cv2.Canny(gray, threshold1=30, threshold2=200)
    cv2.imwrite(img_file_name+'_edges.png', edges)
    print("Detected edges.")
    # Get the coordinates of edge pixels.
    edge_coordinates = np.transpose(np.nonzero(edges))
    # Determine lower contour.
    filtered_coordinates = find_lower_contour(edge_coordinates)
    # Mark lower contour in image and save coordinates to a text file.
    img_bw = largest_component_mask.copy()
    img_bw = cv2.cvtColor(img_bw, cv2.COLOR_GRAY2RGB)
    img = img_original.copy()
    output_file = img_file_name + '_coordinates.txt'
    with open(output_file, 'w') as file:
        for point in filtered_coordinates:
            x, y = point
            cv2.circle(img, (x, y), 2, (0, 0, 255), -1)
            cv2.circle(img_bw, (x, y), 2, (0, 0, 255), -1)
            data_x, data_y = pixel_to_data_point(x, y, x_ref, y_ref)
            file.write(f"{round(data_x, 6)}, {round(data_y, 6)},{x},{y}\n")
    cv2.imwrite(img_file_name + '_with_lower_contour_from_edges.png', img)
    cv2.imwrite(img_file_name + '_with_lower_contour_from_edges_bw.png', img_bw)
    print("Finished: processed image and saved coordinates.")

if __name__ == '__main__':
    main()
