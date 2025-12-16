# Quick Start Guide

## 使用 Java Unit Test Agent

### 在 Claude Code 中使用

1. **打开 Claude Code**
2. **引用此 Agent**：在对话中提及这个 agent 的路径或直接使用预配置的 agent
3. **提供被测试的类**：分享你想要测试的 Java 类代码
4. **描述测试需求**（可选）：如果有特定的测试场景

### 示例对话

```
用户：我需要为这个 UserService 类生成单元测试

[粘贴 UserService.java 代码]

要求：
- 测试所有公共方法
- 包括边界条件和异常场景
- 使用 Mockito mock 依赖
```

Agent 将自动生成：
- ✅ 完整的测试类，包含所有导入
- ✅ 使用 Given-When-Then 命名的测试方法
- ✅ 合适的 Mock 设置
- ✅ AssertJ 断言
- ✅ 测试覆盖说明

### 输出示例

Agent 会生成类似 `examples/UserServiceTest.java` 的完整测试类，包括：

1. **正确的测试结构**
   - @RunWith(MockitoJUnitRunner.class)
   - @Mock 依赖
   - @InjectMocks 被测试类
   - @Before setUp 方法

2. **标准化的方法命名**
   ```java
   givenValidUser_whenCreateUser_thenUserIsSavedAndReturned()
   givenNullUser_whenCreateUser_thenThrowsIllegalArgumentException()
   ```

3. **完整的测试场景**
   - Happy path（正常流程）
   - Edge cases（边界条件）
   - Exception handling（异常处理）
   - Null safety（空值安全）

4. **清晰的 AAA 结构**
   ```java
   // Given - 准备测试数据
   // When - 执行操作
   // Then - 验证结果
   ```

## 本地测试示例

查看 `examples/` 目录下的示例：

```bash
# 查看示例代码
cat examples/UserService.java
cat examples/UserServiceTest.java

# 如果想运行示例测试（需要配置 Gradle wrapper）
make test

# 生成覆盖率报告
make coverage
```

## 配置文件说明

### agent-config.json
定义 agent 的元数据和能力：
- 使用的技术栈版本
- 支持的功能
- 约定和最佳实践
- 覆盖率目标

### prompt.md
Agent 的系统提示词，包含：
- 详细的测试编写规范
- 代码模板
- 最佳实践指南
- 常见场景的示例

### build.gradle
标准的 Gradle 配置，包含：
- Java 8 配置
- JUnit 4.13.2
- Mockito 3.12.4
- AssertJ 3.23.1
- JaCoCo 覆盖率插件

## 测试编写核心原则

### 1. 命名规范（强制）
```java
given<前置条件>_when<执行动作>_then<预期结果>
```

### 2. AAA 结构
```java
@Test
public void givenX_whenY_thenZ() {
    // Arrange (Given)
    // Act (When)
    // Assert (Then)
}
```

### 3. 测试覆盖策略
- ✅ 正常路径
- ✅ 边界条件
- ✅ 异常场景
- ✅ 空值处理

### 4. Mock 策略
- Mock 外部依赖
- 验证方法调用
- 使用 ArgumentCaptor 捕获参数

### 5. 断言最佳实践
- 使用 AssertJ 流式 API
- 每个测试至少一个断言
- 避免过度断言

## 进阶使用

### 自定义测试场景

```
用户：为 PaymentService.processPayment() 方法生成测试

特殊要求：
1. 测试并发场景
2. 测试支付超时
3. 测试重试逻辑
4. 模拟网络异常
```

### 重构现有测试

```
用户：重构这个测试类，使其符合 Given-When-Then 规范

[粘贴现有测试代码]
```

### 添加参数化测试

```
用户：为这个计算方法添加参数化测试，测试多组输入

[粘贴方法代码]
```

## 常见问题

### Q: 如何测试私有方法？
**A**: 不应该直接测试私有方法。通过测试公共方法间接覆盖私有方法。

### Q: 什么时候使用 JUnit 4 vs JUnit 5？
**A**: 
- 默认使用 JUnit 4（向后兼容性好）
- 新项目推荐 JUnit 5（更现代的 API）
- Agent 同时支持两者

### Q: Mock 和 Spy 的区别？
**A**:
- **Mock**: 完全虚拟对象，所有方法需要显式配置
- **Spy**: 包装真实对象，可以选择性 mock 某些方法
- **建议**: 优先使用 Mock

### Q: 如何提高测试覆盖率？
**A**:
1. 使用 `make coverage` 查看覆盖率报告
2. 识别未覆盖的分支和边界条件
3. 添加针对性的测试用例
4. 目标：行覆盖 80%+，分支覆盖 70%+

## 集成到项目

### 1. 将依赖添加到你的 build.gradle

```gradle
dependencies {
    testImplementation 'junit:junit:4.13.2'
    testImplementation 'org.mockito:mockito-core:3.12.4'
    testImplementation 'org.assertj:assertj-core:3.23.1'
}
```

### 2. 配置测试任务

```gradle
test {
    testLogging {
        events "passed", "skipped", "failed"
    }
}
```

### 3. 添加覆盖率检查

```gradle
plugins {
    id 'jacoco'
}

jacocoTestCoverageVerification {
    violationRules {
        rule {
            limit {
                minimum = 0.80
            }
        }
    }
}
```

## 持续改进

这个 agent 会持续更新以支持：
- [ ] JUnit 5 的更多特性
- [ ] Spring Boot 测试支持
- [ ] REST API 测试
- [ ] 数据库集成测试
- [ ] 性能测试基准

## 反馈和贡献

如果你发现问题或有改进建议，请在项目中提出 issue。
