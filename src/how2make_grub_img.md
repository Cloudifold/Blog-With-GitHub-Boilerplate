---
title: 自己做一个带grub引导的，可以开起OS的img！(踩坑记录)
slug: coding
date: 2020/01/06 9:3:00
status: publish
author: cldfd
categories: 
  - coding
tags: 
  - coding
  - boot_load
---
## 自己做一个带grub引导的，可以开起OS的img！(踩坑记录)

### 0x01: GET grubFILE

[grub-0.97-i386]([ftp://alpha.gnu.org/gnu/grub/grub-0.97-i386-pc.tar.gz](ftp://alpha.gnu.org/gnu/grub/grub-0.97-i386-pc.tar.gz))

其他也可以，但是记作一定要用编译好的版本（或者自己编译）

不然后面grub setup会失败……QaQ

<div id="need">我们需要：</div>
**stage1、stage2、与对应文件系统的stage_1_5**

反正我是用的这个版本，没试过grub2……

我这里用的是FAT12文件系统……

### 0x02: make img

```bash
dd if=/dev/zero bs=512 count=2880 of=floppy.img
```

一行`dd`完事，因为建出来的img是空的……

### 0x03: make file system

首先把这个img与某个loop设备相关联.

再开个文件系统.

这里就用loop3作例子好了

```bash
losetup /dev/loop3 floppy.img
mkfs.vfat -F 12 /dev/loop3
```

### 0x04: 挂载文件系统

**随便**找个喜欢的目录挂载：(这里是*/mnt/tst*)

```bash
mkdir /mnt/tst
mount /dev/loop3 /mnt/tst
```

### 0x05: 安装grub的前置工作

建立grub需要的目录结构：

```bash
mkdir -p /mnt/tst/boot/grub
```

把[我们之前说的](#need)需要的grub文件复制到`/mnt/tst/boot/grub`

```bash
cp ./stage1 /mnt/tst/boot/grub
cp ./stage2 /mnt/tst/boot/grub
cp ./fat_stage1_5 /mnt/tst/boot/grub
```

建立两个***必要***的配置文件: // 我安装时没加菜单凉了……qemu能出grub但是出不了OS

**grub.conf**

**menu.lst** 

内容如下：

**grub.conf：** // grub选项

```bash
title TSTOS
root (fd0)
kernel /hx_kernel # kernel path
```

**menu.lst：** // 设置菜单用的

```bash
title TSTOS
root (fd0)
kernel /hx_kernel # kernel path
```

把这两个文件也丢进`/mnt/tst/boot/grub`

```bash
cp ./grub.conf /mnt/tst/boot/grub
cp ./menu.lst /mnt/tst/boot/grub 
```

然后取消挂载

```bash
umount /mnt/tst
```

### 0x06: 在img上安装grub

先得有grub：

```bash
apt install grub
apt_get install grub
```

之后

```bash
grub --device-map=/dev/null

grub> device (fd0) /dev/loop3
grub> root (fd0)
grub> setup (fd0)
grub> quit
```

### 0x07: 解除img与loop设备的关联

```bash
losetup -d /dev/loop3
```
结束！
现在它可以用了1


**附：**
一个脚本：

```bash
#!/bin/bash
dd if=/dev/zero bs=512 count=2880 of=floppy.img

losetup /dev/loop3 floppy.img
mkfs.vfat -F 12 /dev/loop3
mount /dev/loop3 /mnt/tst
mkdir -p /mnt/tst/boot/grub

cp ./stage1 /mnt/tst/boot/grub
cp ./stage2 /mnt/tst/boot/grub
cp ./fat_stage1_5 /mnt/tst/boot/grub

cp ./grub.conf /mnt/tst/boot/grub
cp ./menu.lst /mnt/tst/boot/grub 

umount /mnt/tst

grub --device-map=/dev/null
# manual
# device (fd0) /dev/loop3
# root (fd0)
# setup (fd0)
# quit
losetup -d /dev/loop3
echo "Done!"
```



## 参考资料:

https://www.cnblogs.com/chaunceyctx/p/7358827.html

https://www.cnblogs.com/WuCountry/archive/2010/01/01/1637344.html

https://blog.csdn.net/RichardGreenhhh/article/details/78087066

https://blog.csdn.net/embed2010/article/details/6010919

https://blog.csdn.net/oXueFeiDeYu/article/details/42317939
