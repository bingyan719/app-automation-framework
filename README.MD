App_Auto_Framework
Developed by myself, used it in my previous company, and it can support over 2000 UI test cases.
------------------------------------


### Android执行命令

```
python3 -m ui.cli --device S2D0219126008969 --ftp_name apk-187BEB75916945E2.apk --mode debug --env uimonitorsandbox --project smt --task_token 0EA9ED14179A4079876E190445368515
```

指定测试用例集以及测试用例ID

```
python3 -m ui.cli --device S2D0219126008969 --ftp_name apk-187BEB75916945E2.apk --mode debug --env uimonitorsandbox --project smt --task_token 0EA9ED14179A4079876E190445368515 --specify_cases 登录相关 --case_ids 1
```



```

### 隐藏虚拟键及顶部状态栏：adb

* 隐藏虚拟键及顶部状态栏：

```
adb shell settings put global policy_control immersive.full=*
```

* 隐藏顶部状态栏（底部虚拟键会显示）：

```
adb shell settings put global policy_control immersive.status=*
```

* 隐藏虚拟键（顶部状态栏会显示）：

```
adb shell settings put global policy_control immersive.navigation=*
```

* 恢复原来的设置：

```
adb shell settings put global policy_control null
```
