# vnpy-docker版使用步骤

## 概述

本仓库是自动构建vnpy的开发环境的源代码。构建完vnpy-builder:dev镜像后，使用该镜象中的示例工程可以从交易所获得实时的交易数据。可以作为学习和研究的起步，仅此而已。

运行环境需要mysql环境，因此先部署mysql容器，然后在容器中手动创建vnpy数据库。接下来可以构件vnpy-builder:dev的镜像。 最后用此镜像创建一个容器，运行/app/main.py查看示例的运行情况

## 步骤

 - 部署 mysql
 
 ``` bash 
  ./mysql
 ```

进入mysql容器，手动创建数据库vnpy，后面会用到。

```
 CREATE SCHEMA `vnpy` DEFAULT CHARACTER SET utf8 COLLATE utf8_unicode_ci ;
 create database vnpy default charset utf8 collate utf8_unicode_ci;
```

- 构建镜像

```bash
./build
```

- 创建容器
```bash
 ./debug
```


- 运行示例程序

``` bash
docker exec -it vnpy-builder bash
python main.py
```

## 其它
由于国内无法直接访问交易所，因此需要科学上网，通过http代理的方式访问。也可以直接在国外的服务器上运行，这样省时省力。


## 源代码
https://github.com/stonejiang208/vnpy-docker
