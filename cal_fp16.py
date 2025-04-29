import numpy as np
import struct

def read_hex_file(file_path):
    """读取文件中的16进制数据并转换为FP16浮点数数组"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    
    print(f"文件 {file_path} 中的行数: {len(lines)}")
    print(f"第一行数据: {lines[0].strip()}")
    
    # 只取每行的低16位（后4个字符）
    hex_data = [line.strip()[-4:] for line in lines]
    print(f"提取的前几个16进制字符串: {hex_data[:5]}")
    
    # 确保每个16进制字符串长度为4（代表2字节）
    for i, hex_str in enumerate(hex_data):
        if len(hex_str) != 4:
            print(f"警告: 第{i+1}行的16进制字符串长度不是4: {hex_str}")
            # 补齐或截断到4个字符
            hex_data[i] = hex_str.zfill(4)[-4:]
    
    # 将16进制字符串转换为字节数据
    byte_data = b''.join([bytes.fromhex(hex_str) for hex_str in hex_data])
    print(f"字节数据长度: {len(byte_data)} 字节")
    
    # 检查字节数据是否为2的倍数（FP16需要2字节对齐）
    if len(byte_data) % 2 != 0:
        print("警告: 字节数据长度不是2的倍数，添加一个0字节")
        byte_data += b'\x00'
    
    # 使用numpy的uint16和float16之间的转换来处理FP16数据
    # 尝试小端序
    uint16_array_le = np.frombuffer(byte_data, dtype=np.uint16)
    float16_array_le = uint16_array_le.view(dtype=np.float16)
    
    # 尝试大端序
    uint16_array_be = np.frombuffer(byte_data, dtype='>u2')
    float16_array_be = uint16_array_be.view(dtype='>f2')
    
    print(f"小端序uint16数组前几个值: {uint16_array_le[:5]}")
    print(f"小端序float16数组前几个值: {float16_array_le[:5]}")
    print(f"大端序uint16数组前几个值: {uint16_array_be[:5]}")
    print(f"大端序float16数组前几个值: {float16_array_be[:5]}")
    
    # 默认使用小端序，如果需要大端序，请修改这里
    return float16_array_be  # 或者 return float16_array_be

# 假设矩阵维度已知（示例值，可根据实际需求修改）
m = 8  # SRC1的行数，SRC3的行数
n = 16  # SRC1的列数，SRC2的行数
p = 32  # SRC2的列数，SRC3的列数

# 读取并重塑SRC1矩阵
src1_data = read_hex_file('./Rand_input/SRC1.txt')
print(f"SRC1数据长度: {len(src1_data)}, 预期长度: {m*n}")
assert len(src1_data) == m * n, "SRC1.txt中的元素数量应为m*n"
src1_matrix = src1_data.reshape(m, n)

# 读取并重塑SRC2矩阵
src2_data = read_hex_file('./Rand_input/SRC2.txt')
print(f"SRC2数据长度: {len(src2_data)}, 预期长度: {n*p}")
assert len(src2_data) == n * p, "SRC2.txt中的元素数量应为n*p"
src2_matrix = src2_data.reshape(n, p)

# 读取并重塑SRC3矩阵
src3_data = read_hex_file('./Rand_input/SRC3.txt')
print(f"SRC3数据长度: {len(src3_data)}, 预期长度: {m*p}")
assert len(src3_data) == m * p, "SRC3.txt中的元素数量应为m*p"
src3_matrix = src3_data.reshape(m, p)

# 执行矩阵乘法并加上SRC3
# 注意：为了保持精度，我们先将数据转换为float32进行计算，然后再转回float16
src1_f32 = src1_matrix.astype(np.float32)
src2_f32 = src2_matrix.astype(np.float32)
src3_f32 = src3_matrix.astype(np.float32)

# 检查输入数据是否包含NaN或Inf
if np.isnan(src1_f32).any() or np.isinf(src1_f32).any():
    print("警告: SRC1包含NaN或Inf值")
if np.isnan(src2_f32).any() or np.isinf(src2_f32).any():
    print("警告: SRC2包含NaN或Inf值")
if np.isnan(src3_f32).any() or np.isinf(src3_f32).any():
    print("警告: SRC3包含NaN或Inf值")

# 执行矩阵乘法
dot_result = np.dot(src1_f32, src2_f32)

# 检查乘法结果
if np.isnan(dot_result).any() or np.isinf(dot_result).any():
    print("警告: 矩阵乘法结果包含NaN或Inf值")
    # 替换NaN和Inf值为0
    dot_result = np.nan_to_num(dot_result, nan=0.0, posinf=65504.0, neginf=-65504.0)

# 执行加法
result_f32 = dot_result + src3_f32

# 检查加法结果
if np.isnan(result_f32).any() or np.isinf(result_f32).any():
    print("警告: 加法结果包含NaN或Inf值")
    # 替换NaN和Inf值为0
    result_f32 = np.nan_to_num(result_f32, nan=0.0, posinf=65504.0, neginf=-65504.0)

# 将结果限制在FP16的范围内，避免溢出
fp16_max = np.float32(65504)
fp16_min = np.float32(-65504)
result_f32 = np.clip(result_f32, fp16_min, fp16_max)

# 转换为FP16
result_matrix = result_f32.astype(np.float16)

# 将结果展平为一维数组
result_data = result_matrix.flatten()

# 打印结果数据（浮点数格式和十六进制格式）
print("\n计算结果（浮点数和十六进制格式）:")
print("形状:", result_matrix.shape)
print("数据类型:", result_matrix.dtype)
print("\n结果矩阵:")
for i in range(m):
    print(f"行 {i+1}:", end=" ")
    for j in range(p):
        # 获取浮点数值
        float_val = result_matrix[i, j]
        # 获取十六进制表示
        hex_val = format(float_val.view('<u2'), '04x')
        print(f"{float_val:.6f}(0x{hex_val})", end=" ")
    print()  # 换行

# 打印前20个结果值（如果结果太多）
if len(result_data) > 20:
    print("\n前20个结果值:")
    for i in range(20):
        float_val = result_data[i]
        hex_val = format(float_val.view('<u2'), '04x')
        print(f"索引 {i}: {float_val:.6f} (0x{hex_val})")
    print(f"... 共 {len(result_data)} 个值")
else:
    print("\n所有结果值:")
    for i, float_val in enumerate(result_data):
        # Corrected line: remove [0]
        uint16_val = float_val.view('<u2')
        hex_val = format(uint16_val, '04x')
        print(f"索引 {i}: {float_val:.6f} (0x{hex_val})")

# 将结果保存为16位16进制格式（大端序）
with open('./Result_data/python_fp16.txt', 'w') as f:
    for num in result_data:
        # 将float16转换为大端序的uint16
        # Corrected line: remove [0]
        uint16_val = num.view('<u2')
        hex_str = format(uint16_val, '04x')
        f.write(hex_str + '\n')

print("计算完成，结果已保存到 ./Result_data/python_fp16.txt")