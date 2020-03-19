---
title: 编译和安装Linux内核模块
date: 2020/03/16 00:10:00
status: publish
author: cldfd
categories: 
  - coding
tags: 
  - coding
  - kernel
---

0x01--获取**当前linux内核**源代码

直接`apt-get install linux-source`（这样做会下载到`/lib/modules/$(shell uname -r)`

或者下载当前内核版本的源码（网上乱找）

> 获取内核版本 `uname -a`或`uname -r`

0x02--编写驱动程序的**Makefile**文

把这个makefile和你的module放在同一个目录.

```makefile
ifneq ($(KERNELRELEASE),)
# complie <your module's name>.c
# obj-m := <your module's name>.o
obj-m := hello.o
else
# KERNELDIR := <your path to kernel>/build
KERNELDIR := /lib/modules/$(shell uname -r)/build
PWD := $(shell pwd)

all:
	make −C $(KERNELDIR) M=$(PWD) modules
clean:
	make -C $(KERNELDIR) M=$(PWD) clean
# 缩进是必要的
endif
```

执行该Makefile文件时将跑到 KERNELDIR下调用make.

PWD指定要编译的驱动程序源文件所在的目录，$(shell pwd) 表示当前目录.

0x03--编写内核模块

```C
#include<linux/module.h>
#include<linux/kernel.h>
#include<linux/init.h>

static int __init hello_init(void)
{
        printk("Hello world");
        return 0;
}
static void __exit hello_exit(void)
{
        printk("Goodbye world");
}

module_init(hello_init);// 指定模块初始化函数
module_exit(hello_exit);// 指定模块卸载(退出)函数

MODULE_LICENSE("GPL");  
```

保存为`<module name>.c`就可以啦.

(我这里是`hello.c`)

0x04--编译，安装，卸载，查看

编译：`make`

安装：`insmod <module name>`或`modprobe <module>`(详细用法请参阅命令帮助和相关文档)

卸载：`rmmod <module name>`或`modprobe -r <module name>`

查看：`lsmod | grep <module name>` 、`modinfo <module name>.ko`

（可以`dmesg`查看`printk`打印的消息）

