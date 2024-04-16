### IN PROGRESS:
- update cutout + cutmix (done)
    - failed preliminary: cutmix happens, but bounding box seems wrong
    - try testing on local computer and just the cutmix function


### TODO:
- look at paper https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10122545
- combine bike videos: 
    616459
    677203
    618275
- coco trained vs base class trained 

### OLD (DONE):
- data label for FSL is wrong (corrected)


## Notes:
> ### April 15, 2024

- Finished labeling bottom bracket. I'm gonna walk in front of a bus.
- Some things I could work on to improve inference speed is to modify the model itself. [This paper](https://ieeexplore.ieee.org/stamp/stamp.jsp?tp=&arnumber=10122545) mentions reducing one of the heads. I will try that.
- TODO for tmr: 

    - send video to training. If the queue is too long, worst case I'll run on Google Colab. I want to get this done by tmr so Aaron/Anoushka have time to make something?

    - download and convert bike videos. Start train on tiny + reg model. 


> ### April 13, 2024

some debugging code:
```
# debug local
r = np.random.randint(30)
cv2.imwrite(f"./test_images/img_rgb_{r}.png", cv2.cvtColor(mosaic, cv2.COLOR_BGR2RGB))  # cv2 save
with open(f'./test_images/img_rgb_{r}.txt', 'w') as f:
    f.write(f"target pre boxes: {targets}")
print("im crying")
```

label shows the cutmix labels are just wrong (1,0,0,0) when it should've been fractional. 
My plan is to retrace the target parameter and see what I find, because obviously after exiting the cutmix, everything
looks kinda fine? (OR DOES IT. brb imma check. I can verify this by checking it against normal expected output)

Expected:
```
mix boxes: [[          2      295.51      367.52      434.04       401.4]
 [          0      558.33      578.08         640         640]
 [          1      552.67       563.8         640         640]
 [          1       188.3      601.02       317.1         640]
 [          5      286.34      608.79      410.71         640]
 [          5           0      203.77      38.792         298]]
```

Actual:
```
mix boxes: [[  4 568  58 640 161]
 [  1 407 281 640 530]
 [  5 331 381 640 640]
 [  1 208 110 425 262]]
 ```

 Is it because I shouldn't have integer-ed it???? How does that even make any sense???

 OK i've changed it :
 ```
 mix boxes: [[          0      97.336      259.98      315.49      287.44]
 [          6      606.35      55.404         640      95.966]
 [          0      419.57      159.76      449.83      187.16]
 [          6      588.32      512.46         640      619.26]
 [          0      419.57      393.41      472.13      471.52]]
 ```

 OK anyway moving on to verify the second part (post all augmentations):

 ```
 expected:
 [Mix] labels: [[          1     0.50692     0.51277     0.86326     0.32922]
 [          5      0.4126     0.21782     0.82521     0.32485]
 [          6     0.47599    0.073938     0.18067    0.088958]
 [          1     0.70622    0.093112     0.31014    0.056933]
 [          1     0.54281     0.95798     0.54441    0.084041]]

 actual:
[Cutmix] labels: [[          1     0.84333     0.37007     0.31335     0.14114]
 [          5     0.84878     0.13694     0.30245     0.19075]
 [          2    0.075626     0.53368     0.15125    0.033672]
 [          4     0.93211     0.88964    0.092458    0.056948]
 [          4     0.99285     0.89165    0.014295    0.058288]]
```

OK ngl at this point is probably the INTEGER, cuz it rounded all the division/addition to 1/0, hence all labels became useless.

Yup it's the `dtype=int` in the cutmix method. Bruh. I love being a code monkey. 