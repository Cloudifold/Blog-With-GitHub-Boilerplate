---
title: cldfd的朋友们
slug: linux-slab
date: 2020/03/19 19:05:00
status: publish
author: cldfd
categories: 
  - coding
tags: 
  - coding
  - linux
  - memory manage
---


# **0.前置说明**

(为什么要扯缓存呢？因为slab分配器实际上就是一种缓存)

**缓存**：缓存是一种用于"存放并管理可用的、**已分配好**的对象"的对象。

缓存是为了方便对象的频繁分配(创建)与回收(销毁)而存在的。

对缓存来说重要的是存储(不然为什么叫缓存呢)，当代码需要新的对象时可以直接从缓存中获取，而代码不再需要这个对象时就把它放回缓存。

简单来说缓存就像存纸的纸堆，对象就相当于一张纸。 代码需要操作对象(在纸上写字)就要从纸堆中抽纸，纸不用了就擦干净(放回缓存)之后放回纸堆。 不使用缓存就像用纸时从造纸厂拿纸(分配对象)，不用纸了就放回造纸厂回炉(销毁对象)一样效率低下。

一般会专门为某一种对象提供缓存，比如专为inode结构体设立的缓存。当代码要分配一个新的inode时就从这个缓存中获取。



用空闲链表来实现缓存是比较方便的一种选择。

在**内核**中，空闲链表面临的主要问题之一是**不能全局控制**。当可用内存紧缺时，内核无法通知空闲链表，让空闲链表收缩缓存的大小以便释放部分内存。

为了弥补这一缺陷，Linux提供了slab分配器来**实现**缓存。

------

# **1.slab分配器的基本设计思想**

摘自《LINUX内核设计与实现》

> slab分配器试图在几个基本原则间寻求平衡：

- 频繁使用的数据结构也会频繁分配和释放，所以应当缓存它们。
- 频繁分配和回收必然会频繁分配和释放必然导致内存碎片（难以找到大块连续的可用内存）。为了避免这种现象，空闲链表的缓存会连续地存放。因为已释放的数据结构又会放回空闲链表，因此不会导致碎片。
- 回收的对象可以立刻投入下一次分配，因此，对于频繁的分配和释放，空闲链表能够提高其性能。
- 如果分配器知道对象大小，页大小和总的高速缓存的大小这样的概念，它回做出更明智的决策。
- 如果让部分缓存专属于单个处理器（对系统上的每个处理器独立且唯一），那么，分配和释放就可以在不加SMP锁的情况下进行。
- 如果分配器是于NUMA相关的，它就可以从相同的内存节点为请求者进行分配。
- 对存放的对象进行着色（colored），以防多个对象映射到相同的高速缓存行（cache line）。

------

# **2.slab层的设计**

slab层把不同的对象划分为**高速缓存**(kmem_cache)组，每个高速缓存都存放不同类型的对象。

比如说，一个高速缓存用来存放inode结构体。

然后，这些高速缓存被划分为slab，slab由一个或多个**物理上连续的页**组成。

每个slab包含一些对象的实例，每个slab有三种状态：空、部分满、满。一个满的slab没有空闲的对象，一个空的slab所有对象都是空闲的。

内核某一部分需要一个新的对象时，slab分配器会优先从部分满的slab中分配。如果没有部分满的slab就从空的slab中分配。如果没有空的slab就创建一个空的slab。

------

# **3.使用slab**

**本文使用内核版本为linux-source-5.4**

为了使用slab，我们首先需要为一种对象创建一个高速缓存(kmem_cache)。

调用``kmem_cache_create`创建一个高速缓存(在`include/linux/slab.h`第395行声明)

```
struct kmem_cache *kmem_cache_create(const char *name, unsigned int size,
			unsigned int align, slab_flags_t flags,
			void (*ctor)(void *));
```

返回一个指向`struct kmem_cache`类型的指针。

要分配空间的话只需要调用`kmem_cache_alloc`函数(在`include/linux/slab.h`第394行声明)。

这个过程其实就使用了slab分配器分配空间。

```
void *kmem_cache_alloc(struct kmem_cache *, gfp_t flags) __assume_slab_alignment __malloc;
```

这个函数以一个指向`struct kmem_cache`类型的指针和一个标志(flags)来分配空间，返回一个指向`void`类型的指针。

这样你就可以得到一个大小为`size`的可用空间(这个size是kmem_cache_alloc根据第一个参数决定的)。

可以通过`kmem_cache_free`来释放你得到的空间(在`include/linux/slab.h`第395行声明)。

```
void kmem_cache_free(struct kmem_cache *, void *);/* 后面这个是那个分配得来的指针 */
```

调用函数`kmem_cache_destroy`销毁你创建的`kmem_cache`结构体(在`include/linux/slab.h`第165行声明)。

```
void kmem_cache_destroy(struct kmem_cache *);
```

我们可以写出以下代码示例来使用slab分配器分配结构体。

```c
#include <linux/init.h> 
#include <linux/module.h> 
#include <linux/module.h> 

#include <linux/unistd.h>
//#include <sys/type.h>
#include <linux/slab.h>
#include <linux/slab_def.h>
MODULE_LICENSE("GPL");  

#define OBJNUM   1000     /* the number of objects to be allocated */
#define PRINT_INTERVAL 250

static int sample_struct_num; /* how many times sample_struct_ctor will be used */


struct sample_struct {
    int id;
    char firstname[0x10];
    char lastname[0x10];
};


static struct kmem_cache *sample_struct_cachep;

/* store pointers points struct sample_struct */
static struct sample_struct *sample_struct_pool[OBJNUM];

/* constructor of struct_ctor */
static void sample_struct_ctor(void *cachep)
{
    ((struct sample_struct *)cachep)->id = sample_struct_num;
    if (++sample_struct_num %PRINT_INTERVAL == 0 )
    {
        printk (KERN_INFO "inited %d objects", sample_struct_num);
    }
}


static void print_kmem_cache_info_qwq(struct kmem_cache *cachep)
{
    printk ("kmem_cache size : 0x%x\\n", kmem_cache_size (cachep));
    printk ("kmem_cache name : %s\\n", cachep->name);
    printk ("kmem_cache flags : 0x%x\\n", cachep->flags);
    printk ("kmem_cache num of objs per slab : 0x%x\\n", cachep->num);
}


static int sample_mod_init(void)
{
    int i;

    sample_struct_cachep = kmem_cache_create (
            "sample_struct_cachep",         /* Name */
            sizeof(struct sample_struct),   /* Object Size */
            0,                              /* Alignment */
            SLAB_HWCACHE_ALIGN,             /* Flags */
            sample_struct_ctor);            /* Constructor */

    /* check if fail */
    if (NULL == sample_struct_cachep)
    {
        printk (KERN_INFO "Failed to create sample_struct_cachep. -- module slabtest_qwq\\n");
        return 1;
    }

    /* print cache info */
    print_kmem_cache_info_qwq (sample_struct_cachep);

    for (i = 0; i < OBJNUM; i++)
    {
        /* allcote structs */
        sample_struct_pool[i] = kmem_cache_alloc (sample_struct_cachep, GFP_KERNEL);

        /* print message if fail */
        if (NULL == sample_struct_pool[i])
        {
            printk ("Object %d alloc ERROR.  -- module slabtest_qwq \\n", i);
            sample_struct_pool[i] = NULL;
        }
        else if (i % PRINT_INTERVAL == 0)
        {
            printk ("sample_struct_pool[%d]->id = %d", i, sample_struct_pool[i]->id);
        }
    }   
print_kmem_cache_info_qwq (sample_struct_cachep);
    return 0;
}


static void sample_mod_exit(void)
{
    int i;

    printk (KERN_INFO "Destroying sample_structs!\\n");
    for (i = 0; i < OBJNUM; i++)
    {
        /* check */
        if (sample_struct_pool[i] != NULL)
        {
            kmem_cache_free (sample_struct_cachep, sample_struct_pool[i]);
            sample_struct_pool[i] = NULL;
        }
    }

    if (sample_struct_cachep != NULL) 
    {
        /* destroy */
        kmem_cache_destroy (sample_struct_cachep);
        printk (KERN_INFO "Destroyed sample_struct_cachep!\\n");
    }
    print_kmem_cache_info_qwq (sample_struct_cachep);
    return ;
} 

module_init (sample_mod_init); 
module_exit (sample_mod_exit);

MODULE_AUTHOR ("cldfd"); 
MODULE_DESCRIPTION("Slab sample");
```

编译并装载内核模块后可以通过`dmesg`命令查看`printk`打印出的消息。

以下为装载模块并卸载模块后`dmesg`的查看结果。

# **4.slab的实现解析(概述)**
