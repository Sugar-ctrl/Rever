# Rever 语言语法规范

## 基本语法规则

### 1. 值和引用
```
x        # 获取变量x的值
&x       # 获取变量x的引用
ptr @    # 解引用指针
```

### 2. 赋值语法
```
42 &x =      # 变量赋值：x = 42
3 4 + &y =   # 表达式赋值：y = 7
```

### 3. 成员访问（带空格分隔）
```
obj .attr     # 访问对象属性
obj .method ! # 调用对象方法
ptr @ .attr   # 通过指针访问属性
```

### 4. 注释
```
# 行注释
##
多行
注释 # 可以包含行注释
##
```

## 数据类型操作

### 1. 列表操作（需要指针）
```
# 创建列表（返回列表指针）
1 2 3 3 list &myList =  # &myList 指向列表[1, 2, 3]

# 访问列表元素
0 myList .get !      # 获取第一个元素：1
10 1 myList .set !   # 设置第二个元素为10

# 列表长度
myList .len !        # 获取列表长度：3

# 添加元素
4 myList .append !   # 列表变为[1, 10, 3, 4]
```

### 2. 字典操作
```
# 创建字典（返回字典指针）
"name" "John" "age" 30 2 dict &myDict =

# 访问字典元素
"name" myDict .get !     # "John"
"Alice" "name" myDict .set !  # 设置name为"Alice"
```

### 3. 字符串操作
```
"hello" " world" + &greeting =  # 字符串连接
0 greeting .get !              # 获取第一个字符：'h'
```

## 函数定义和调用

### 1. 函数定义
```
# 基本函数
{
  &y = &x = x y + return
} &add =  # 函数赋值

# 语法糖
{
  y = x = x y + return
} add def  # 等价于 &add =

# 可变参数函数
{
  &n = 0 &sum =
  0 &i =  # 添加索引变量
  { i n < }
  {
    &arg = arg sum + &sum =
    1 i + &i =  # 更新索引
  } while
  sum return
} &sum =
```

### 2. 函数调用
```
3 4 add !      # 直接调用：7
3 4 &add @ !   # 通过引用调用：7
```

## 控制流

### 1. 条件判断
```
x 0 >
{
  "positive" print !
}
{
  "non-positive" print !
} ifelse
```

### 2. 循环
```
# while循环
0 &i =
{
  i 10 <
}
{
  i print !
  1 i + &i =
} while

# for循环用while实现，基本与上方相同
```

## 面向对象编程

### 1. 类定义
```
{
  # 构造函数
  {
    &self = &age = &name =
    name self .&name =
    age self .&age =
  } __init__ def

  # 方法
  {
    &self =
    "Hello, " self .name + "!" + print !
  } greet def

} &Person class
```

### 2. 对象操作
```
# 创建对象（返回对象）
"John" 30 Person ! &person =

# 属性访问
person .name     # "John"
"Alice" person .&name =  # 设置name

# 方法调用
person .greet !  # 调用方法
```

### 3. 继承
```
{
  Person super !

  {
    &self = &title = &age = &name =
    name self .&name =
    age self .&age =
    title self .&title =
  } __init__ def

  {
    &self =
    "I'm " self .name + ", the " self .title + "!" + print !
  } greet def

} &Employee class
```

## 指针高级操作

### 1. 多级指针
```
&x &ptr1 =     # ptr1 指向x
&ptr1 &ptr2 =  # ptr2 指向ptr1
ptr2 @ @       # 双重解引用：x的值
```

### 2. 动态数据结构
```
# 链表节点
{
  {
    &self = &next = &data =
    data self .&data =
    next self .&next =
  } __init__ def
} &Node class

# 创建链表
null &tail =
10 &tail Node ! &node3 =
20 &node3 Node ! &node2 =
30 &node2 Node ! &head =

# 遍历链表
head &current =
{
  current null !=
}
{
  current .data print !
  current .next @ &current =
} while
```

### 3. 函数指针表
```
# 创建函数指针数组
&add &funcs 0 set !
&sub &funcs 1 set !
&mul &funcs 2 set !

# 通过索引调用
3 4 funcs 0 get ! @ !  # add(3, 4)
```

## 内置函数和操作符
将作为builtin工具函数，后期再做

### 1. 栈操作
```
dup    # 复制栈顶元素
swap   # 交换栈顶两个元素
drop   # 丢弃栈顶元素
over   # 复制栈顶第二个元素
```

### 2. 类型检查
```
42 type !  # "int"
"hello" type !  # "string"
&x type !  # "pointer"
```

### 3. 输入输出
```
"Enter name: " print !
read ! &name =  # 读取输入
"Hello, " name + print !
```

## 完整示例

### 阶乘函数
```
{
  &n =
  n 0 ==
  { 1 return }
  { n n 1 - factorial ! * return }
  ifelse
} factorial def

5 factorial ! print !  # 120
```

### 列表处理
```
# 创建并处理列表
1 2 3 4 4 list &numbers =
0 &sum =
numbers .len ! &length =  # 先保存长度
0 &i =  # 添加索引变量
{ i length < }
{
  i numbers .get ! sum + &sum =
  1 i + &i =  # 更新索引
} while
sum print !
```

### 对象系统示例
```
# 创建员工对象
"Alice" 28 "Manager" Employee ! &employee =
employee .greet !  # "I'm Alice, the Manager!"

# 多态示例
&employee &personRef =
personRef .greet !  # 仍然调用Employee的greet方法
```

## 语法总结表

| 操作 | 语法 | 示例 |
|------|------|------|
| 变量赋值 | `值 &变量 =` | `42 &x =` |
| 引用获取 | `&变量` | `&x` |
| 解引用 | `指针 @` | `ptr @` |
| 成员访问 | `对象 .属性` | `obj .attr` |
| 指针成员 | `指针 @ .属性` | `ptr @ .attr` |
| 方法调用 | `对象 .方法 !` | `obj .method !` |
| 列表创建 | `元素 n list` | `1 2 3 3 list` |
| 函数定义 | `{代码} &函数 =` | `{ + return } &add =` |