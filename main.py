import ov2640
import gc
import time
import sys

FNAME = '1024x768_200milliseconds.jpg'

def main():
    try:
        #cam = ov2640.ov2640(resolution=ov2640.OV2640_320x240_JPEG)
        #cam = ov2640.ov2640(resolution=ov2640.OV2640_640x480_JPEG)
        cam = ov2640.ov2640(resolution=ov2640.OV2640_1024x768_JPEG)
        #cam = ov2640.ov2640(resolution=ov2640.OV2640_1600x1200_JPEG)
        print("ram free in bytes", gc.mem_free())
    
        clen = cam.capture_to_file(FNAME, True)
        print("captured image is %d bytes" % clen)
        print("image is saved to %s" % FNAME)
    
        time.sleep(1)
        sys.exit(0)
    
    except KeyboardInterrupt:
        sys.exit(0)


if __name__ == '__main__':
    main()

