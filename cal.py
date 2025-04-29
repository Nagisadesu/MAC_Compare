import numpy as np
import struct

def read_hex_file(file_path):
    """读取文件中的16进制数据并转换为FP32浮点数数组"""
    with open(file_path, 'r') as f:
        lines = f.readlines()
    hex_data = [line.strip() for line in lines]
    byte_data = b''.join([bytes.fromhex(hex_str) for hex_str in hex_data])
    float_array = np.frombuffer(byte_data, dtype='>f4')
    return float_array

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
result_matrix = np.dot(src1_matrix, src2_matrix) #+ src3_matrix

# 将结果展平为一维数组
result_data = result_matrix.flatten()

# 将结果保存为32位16进制格式
with open('./Result_data/python.txt', 'w') as f:
    for num in result_data:
        byte_data = struct.pack('!f', num)
        hex_str = byte_data.hex()
        f.write(hex_str + '\n')