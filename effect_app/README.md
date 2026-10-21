# How to create a video 

1. set black background
2. install `byzanz`
3. run the following code in terminal (`fish` shell):

```
for i in $(seq 1 77)
  echo $i
  byzanz-record /path/to/effect$i.webm -e "./eff_tester.py $i" -h 18 -w 1480 -x 20 -y 18
end
```
4. (optional) use `ffmpeg` to convert webm to gif

```
for i in /path/to/*webm; do ffmpeg -i $i -pix_fmt rgb24 (path change-extension gif $i); end
```
