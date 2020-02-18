import cv2
 
def decode_segmap(image, source, nc=21):
    # Load the foreground input image
    foreground = cv2.imread(source)
 
    # Change the color of foreground image to RGB
    # and resize image to match shape of R-band in RGB output map
    foreground = cv2.cvtColor(foreground, cv2.COLOR_BGR2RGB)
    foreground = cv2.resize(foreground,(r.shape[1],r.shape[0]))
 
    # Create a background array to hold white pixels
    # with the same size as RGB output map
    background = 255 * np.ones_like(rgb).astype(np.uint8)
 
    # Convert uint8 to float
    foreground = foreground.astype(float)
    background = background.astype(float)
 
    # Create a binary mask of the RGB output map using the threshold value 0
    th, alpha = cv2.threshold(np.array(rgb),0,255, cv2.THRESH_BINARY)
 
    # Apply a slight blur to the mask to soften edges
    alpha = cv2.GaussianBlur(alpha, (7,7),0)
 
    # Normalize the alpha mask to keep intensity between 0 and 1
    alpha = alpha.astype(float)/255
 
    # Multiply the foreground with the alpha matte
    foreground = cv2.multiply(alpha, foreground)
 
    # Multiply the background with ( 1 - alpha )
    background = cv2.multiply(1.0 - alpha, background)
 
    # Add the masked foreground and background
    outImage = cv2.add(foreground, background)
 
    # Return a normalized output image for display
    return outImage/255