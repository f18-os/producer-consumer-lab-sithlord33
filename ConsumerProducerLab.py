import threading
import cv2
import os
import base64
import queue

#globals
frames = []
q2 = []
l1 = threading.Lock()
l2 = threading.Lock()
se1 = threading.Semaphore(10)
se2 = threading.Semaphore(10)
sf1 = threading.Semaphore(10)
sf2 = threading.Semaphore(10)

class extractFrames(threading.Thread):
    def _init_(self):
        super(extractFrames, self)._init_()

    def run(self):
        clipFileName = 'clip.mp4'
        
        #initialize frame count
        count = 0

        #open video file
        vidcap = cv2.VideoCapture(clipFileName)

        #read first image
        success, image = vidcap.read()

        print("Reading frame {} {} ".format(count, success))
        count += 1

        while success:
            se1.acquire()
            l1.acquire()
            frames.append(image)
            success, image = vidcap.read()
            print('Reading frame {} {}'.format(count))
            count += 1
            l1.release()
            sf1.release()

        for i in range(10):
            print("Releasing f1 ", i)
            sf1.release()

class convertToGrayscale(threading.Thread):
    def _init_(self):
        super(convertToGrayscale, self)._init_()

    def run(self):
        #initialize frame count
        count = 0

        while True:
            sf1.acquire()
            se1.acquire()
            l1.acquire()
            l2.acquire()

            if(frames):
                tempF = frames.pop()
            else:
                break
            print('Converting frame {}'.format(count))

            #convert the image to grayscale
            grayScale = cv2.cvtColor(tempF, cv2.COLOR_BGR2GRAY)
            q2.append(grayScale)
            count += 1

            l1.release()
            l2.release()

            sf2.release()
            se1.release()

        l2.release()
        l1.release()
        se1.release()

        for i in range(10):
            print("f2 released ", i)
            sf2.release()

class displayFrames(threading.Thread):
    def _init_(self):
        super(displayFrames, self)._init_()

    def run(self):
        while True:
            sf2.acquire()
            l2.acquire()
            if (q2):
                #display image in queue
                image = q2.pop()
                cv2.imshow("Video", image)

                #wait 42 ms and check if the user wants to quit
                if cv2.waitKey(24) and 0xFF == ord("q"):
                    break
            else:
                print("Done!")
                break
            l2.release()
            se2.release()


for i in range(10):
    sf1.acquire()
    sf2.acquire()

dFrames = displayFrames()
cFrames = convertToGrayscale()
eFrames = extractFrames()

print("Starting thread ------- extract")
eFrames.start()
print("Starting thread ------- convert")
cFrames.start()
print("Starting thread ------- display")
dFrames.start()
