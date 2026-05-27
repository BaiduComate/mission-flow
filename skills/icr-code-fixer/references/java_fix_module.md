# Java语言的典型案例与常见遗漏清单

## Java
    --**禁止修改代码缩进与闭合**
    --**保持当前文档最后一行不变**
    --**修复前代码修复后代码，代码逻辑必须要相同，严禁改写后代码逻辑发生变化**
    --**文件为文件中异常部分，没有在上述问题列表中出现的行号，禁止处理**
    --**严禁编造、推测或主观臆断内容。**

    --** 以下是一些问题修复后示例，以及关注的重点：

          --**## 问题类型：[JAVA018] 列宽需小于180字符；表示当前行长度最大值为180，其中长度需要你通过字符数去计算，一个字符相当于长度为1
               **修复前代码：
                    const extremelyLongVariableNameForTestingMaxLineLengthRule = '这是一段非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常非常长的文本内容用于测试最大行长度限制规则非常长长长长';
               **修复后代码：
                    const extremelyLongVariableNameForTestingMaxLineLengthRule = 
                    '这是一段非常非常非常非常非常非常非常非常非常非常非常非常非常非常
                    非常非常非常非常长的文本内容用于测试最大行长度限制规则非常长长长长';
        --**## 问题类型4：顶层类名称与文件名称不一致
            **规则说明：
                Java要求顶层公共类的类名必须与文件名（不含.java后缀）完全一致（包括大小写）。
                修复时需要根据实际情况判断：
                - 检查顶层类名和文件名各自是否符合 UpperCamelCase（大驼峰）命名规范
                - 优先保留符合命名规范的那一方，修改不符合的一方以保持一致，注意： 你是可以修改文件名的
                - 如果两者都符合规范但互不一致，以顶层类名为准，注意： 你是可以修改文件名的
            **注意事项：
                - 修改类名时，同步更新所有对该类的引用（import语句、实例化代码等）
                - 修改文件名时，同步更新构建配置（如 build.gradle、pom.xml）中的引用
                - 如果类名修改涉及 Spring 注解（如 @Component("originalName")），保持注解中的名称不变
                - 修复后确保 类名 == 文件名（不含.java），且两者都符合 UpperCamelCase（大驼峰）命名规范


        --**## 问题类型5：Object 的 equals 方法容易抛空指针异常，应使用常量或确定有值的对象来调用 equals。
                **修复前代码：
                    object.equals("test");
                **修复后代码：" 
                    "test".equals(object);" +

        --**## 问题类型：在非空代码块中使用花括号时要遵循K&R风格
                **修复前代码：
                    System.out.println("Bad example"); }
                    private String name;
                    public BadExample() {
                **修复后代码：
                    System.out.println("Bad example");
                    }
                    private String name;
                    public BadExample() {

        --**## 问题类型6：[javaFixModule]类名必须遵循大写字母开头的驼峰式命名方式[^[A-Z][a-zA-Z0-9]*$]
                **修复前代码：
                    public class javaFixModule {
                **修复后代码：
                    public class JavaFixModule {
                **注：只修改大小写，别改命名的意思

        --**## 问题类型7：[javaFixModule]类、类属性、类方法的注释必须使用Javadoc,禁止使用//注释
                **修复前代码：
                    // Helper method for exceptions
                    private void riskyOperation() throws Exception {
                **修复后代码：
                    /**
                    * Helper method for exceptions
                    * @throws Exception 抛出异常
                    */
                    private void riskyOperation() throws Exception {

        --**## 问题类型8：IgnoredReturnValueCheck 返回值被忽略
                **修复前代码：
                    "test".length();  // 返回值未使用
                **修复后代码：
                    int length = "test".length();  // 使用返回值
                    System.out.println("字符串长度: " + length);

        --**## 问题类型9：BigDecimalConstructedFromDouble BigDecimal构造问题
                **修复前代码：
                    BigDecimal bd = new BigDecimal(0.1);  // 应使用字符串 "0.1"
                **修复后代码：
                    BigDecimal bd = new BigDecimal("0.1");  // 使用字符串构造，避免精度问题

        --**## 问题类型10：NullReference 空指针风险
                **修复前代码：
                    Integer num = null;
                    int value = num;  // 会抛出 NullPointerException
                **修复后代码：
                    Integer num = null;
                    int value = num != null ? num : 0;  // 添加空值检查


        --**## 问题类型11：SynchronizationOnStringOrBoxedCheck 同步锁问题
                **修复前代码：
                    private static final String LOCK = "lock";  
                    public void badSynchronization() {
                        synchronized (LOCK) {  // 违规，String 常量可能被共享
                            // 操作
                        }
                    }
                **修复后代码：
                    private static final Object LOCK = new Object();  // 使用独立的Object对象
                    public void badSynchronization() {
                        synchronized (LOCK) {  // 正确使用
                            // 操作
                        }
                    }

        --**## 问题类型12：SwitchCaseWithoutBreakCheck switch穿透问题
                **修复前代码：
                    switch (value) {
                        case 1:
                            System.out.println("one");
                            // 缺少 break
                        case 2:
                            System.out.println("two");
                            break;
                    }
                **修复后代码：
                    switch (value) {
                        case 1:
                            System.out.println("one");
                            break;  // 添加 break
                        case 2:
                            System.out.println("two");
                            break;
                    }

        --**## 问题类型：ToStringReturningNullCheck toString返回null
                **修复前代码：
                    @Override
                    public String toString() {
                        return null;  // 不应返回 null
                    }
                **修复后代码：
                    @Override
                    public String toString() {
                        return "JavaFixModule{" +
                                "id=" + id +
                                ", name='" + name + '\'' +
                                '}';
                    }
