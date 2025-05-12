import numpy as np
import struct

def read_hex_file(file_path):
    """读取文件中的16进制数据并转换为int8整数数组，考虑到高24位为0"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    hex_data = [line.strip() for line in lines]
    
    # 创建int8数组
    int8_array = np.zeros(len(hex_data), dtype=np.int8)
    
    for i, hex_str in enumerate(hex_data):
        # 从32位hex中提取最低8位（最后2个字符）
        int8_value = int(hex_str[-2:], 16)
        # 处理有符号整数的符号位
        if int8_value > 127:
            int8_value -= 256
        int8_array[i] = int8_value
        
    return int8_array

# 假设矩阵维度已知（示例值，可根据实际需求修改）
m = 8  # SRC1的行数，SRC3的行数
n = 16  # SRC1的列数，SRC2的行数
p = 32  # SRC2的列数，SRC3的列数

# 读取并重塑SRC1矩阵
src1_data = read_hex_file('./Rand_input/SRC1.txt')
assert len(src1_data) == m * n, "SRC1.txt中的元素数量应为m*n"
src1_matrix = src1_data.reshape(m, n)

# 读取并重塑SRC2矩阵
src2_data = read_hex_file('./Rand_input/SRC2.txt')
assert len(src2_data) == n * p, "SRC2.txt中的元素数量应为n*p"
src2_matrix = src2_data.reshape(n, p)

# 读取并重塑SRC3矩阵
src3_data = read_hex_file('./Rand_input/SRC3.txt')
assert len(src3_data) == m * p, "SRC3.txt中的元素数量应为m*p"
src3_matrix = src3_data.reshape(m, p)

# 执行矩阵乘法并加上SRC3
# 注意：使用int32类型进行计算，防止溢出
result_matrix = np.matmul(src1_matrix.astype(np.int32), src2_matrix.astype(np.int32)) + src3_matrix.astype(np.int32)

# 将结果展平为一维数组
result_data = result_matrix.flatten()

# 将结果保存为32位16进制格式
with open('./Result_data/python_int8.txt', 'w') as f:
    for num in result_data:
        # 将int32值转换为32位十六进制字符串
        hex_str = format(np.uint32(num), '08x')
        f.write(hex_str + '\n')