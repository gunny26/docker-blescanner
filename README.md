# BLE Scanner

Container to sniff for some bluetooth low energy events and make them available as metric for prometheus

## how to build

make latest to build image based om amd64 architecuture
the resulting image is not pushed to any registry

this is ideal to develop fast on your machine

make stable builts the image or arm64/v8 supposed to run on Rapsberr Pi
this image will be automatically pushed to docker registry

the stable build needs way more time, the arm64/v8 is emulated by qemu
