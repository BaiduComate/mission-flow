# JavaScript语言的典型案例与常见遗漏清单

## JavaScript/TypeScript
    --**禁止修改代码缩进与闭合**
    --**保持当前文档最后一行不变**
    --**修复前代码修复后代码，代码逻辑必须要相同，严禁改写后代码逻辑发生变化**
    --**文件为文件中异常部分，没有在上述问题列表中出现的行号，禁止处理**
    --**严禁编造、推测或主观臆断内容。**

        --**## 问题类型：'v-model' should be on a new line. 表示要v-model需要另起一行，所以修复需要调整换行
                **修复前代码：
                <el-input size="mini" class="input" v-model="params.templateName"></el-input>
               **修复后代码：
                <el-input size="mini" class="input" 
                       v-model="params.templateName"></el-input>
                        pass
        --**## 问题类型：Trailing spaces not allowed.表示句尾不需要有空格，要删除最后的空格
               **修复前代码：
                    el-input 
               **修复后代码：去掉最后的空格
                    el-input        --**## 问题类型：Attribute ":key" should go before "v-for". 表示元素顺序需要调整
               **修复前代码：
                    <div v-for="(item, ind) in params.hiImgVos" :key="ind">
               **修复后代码：
                    <div :key="ind" v-for="(item, ind) in params.hiImgVos">
        --**## 问题类型：":title" should go before ":close-on-click-modal" 表示元素顺序需要调整
               **修复前代码：
                    :close-on-click-modal="false"
                    :title="dialog.title"
               **修复后代码：
                    :title="dialog.title"
                    :close-on-click-modal="false"
          --**## 问题类型："This line has a length of 123. Maximum allowed is 120" 表示当前行长度最大值为120，其中长度需要你通过字符数去计算，一个字符相当于长度为1
               **修复前代码：
                    const extremelyLongVariableNameForTestingMaxLineLengthRule = '这是一段非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的文本内容用于测试最大行长度限制规则非常长长长长';
               **修复后代码：
                    const extremelyLongVariableNameForTestingMaxLineLengthRule = 
                    '这是一段非常非常非常非常非常非常非常非常非常非常非常非常非常非常
                    非常非常非常非常长的文本内容用于测试最大行长度限制规则非常长长长长';
        --**## 问题类型："Strings must use singlequote." 表示 字符串必须使用单引号
               **修复前代码：
                    const userNameTrailing = "asfdhapif"
               **修复后代码：
                    const userNameTrailing = 'asfdhapif';
        --**## 问题类型："This line has 3 statements. Maximum allowed is 1." 表示 每行最多只允许包含一条语句
               **修复前代码：
                    if (valX === 5) { console.log('valX is 5'); console.log('incrementing'); }
               **修复后代码：
                    if (valX === 5) { 
                    console.log('valX is 5');
                    console.log('incrementing'); 
                    }
        --**## 问题类型："Trailing spaces not allowed." 表示 禁止行尾存在空格，要去掉这一行尾部的所有空格字符
               **修复前代码：
                    const userNameTrailing = 'aaa+';    
               **修复后代码：
                    const userNameTrailing = 'aaa+';
        --**## 问题类型："Arrow function used ambiguously with a conditional expression." 表示 箭头函数与条件表达式（三元运算符）混用时存在歧义
               **修复前代码：
                    const confusingArrow1 = a => 1 ? 2 : 3;
               **修复后代码：
                    const confusingArrow1 = a => (1 ? 2 : 3);
        --**## 问题类型："Missing space before function parentheses." 要求函数名和括号之间添加空格， function 关键字和括号之间添加空格，箭头函数参数和箭头之间添加空格，生成器函数名和括号之间添加空格
               **修复前代码：
                    function fetchData(){
                         return api.getData();
                    }
                    const arrowFunction = (inputValue)=>{
                         return inputValue * 2;
                    };
                    
             **修复后代码：
                    function fetchData () {
                         return api.getData();
                    }
                    const arrowFunction = (inputValue) => {
                         return inputValue * 2;
                    };

        --**## 问题类型："Multiple spaces found before " 表示 混合使用了制表符（Tab）和空格（Space）进行缩进
               **修复前代码：
function mixedIndentationExample() {
  const tabIndented = 100;  
  const spaceIndented = 200; 
  if (tabIndented === 100) {
    console.log(tabIndented);  
    console.log(spaceIndented);  
  }
}
               **修复后代码：
function mixedIndentationExample() {
  const tabIndented = 100;  // 改为2个或4个空格
  const spaceIndented = 200; // 保持空格
  if (tabIndented === 100) {
    console.log(tabIndented);  // 改为空格
    console.log(spaceIndented);  // 改为空格
  }
}

