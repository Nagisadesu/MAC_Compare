#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

// 矩阵维度（示例值，可根据实际需求修改）
#define M 2  // SRC1 的行数，SRC3 的行数
#define N 3  // SRC1 的列数，SRC2 的行数
#define P 2  // SRC2 的列数，SRC3 的列数

// 读取 16 进制文件并转换为浮点数数组
int read_hex_file(const char *filename, float *data, int expected_size) {
    FILE *file = fopen(filename, "r");
    if (!file) {
        fprintf(stderr, "无法打开文件 %s\n", filename);
        return 0;
    }

    char line[16];
    int i = 0;
    while (fgets(line, sizeof(line), file) && i < expected_size) {
        line[strcspn(line, "\n")] = 0; // 移除换行符
        if (strlen(line) != 8) {
            fprintf(stderr, "文件 %s 第 %d 行格式错误\n", filename, i + 1);
            fclose(file);
            return 0;
        }
        uint32_t hex_value;
        sscanf(line, "%x", &hex_value);
        // 将 32 位整数解释为浮点数
        memcpy(&data[i], &hex_value, sizeof(float));
        i++;
    }

    fclose(file);
    if (i != expected_size) {
        fprintf(stderr, "文件 %s 数据量不足，期望 %d，实际 %d\n", filename, expected_size, i);
        return 0;
    }
    return 1;
}

// 矩阵乘法：result = A * B
void matrix_multiply(float *A, float *B, float *result, int m, int n, int p) {
    for (int i = 0; i < m; i++) {
        for (int j = 0; j < p; j++) {
            float sum = 0.0f;
            for (int k = 0; k < n; k++) {
                sum += A[i * n + k] * B[k * p + j];
            }
            result[i * p + j] = sum;
        }
    }
}

// 矩阵加法：result += C
void matrix_add(float *result, float *C, int m, int p) {
    for (int i = 0; i < m * p; i++) {
        result[i] += C[i];
    }
}

// 保存结果为 16 进制格式
void save_hex_file(const char *filename, float *data, int size) {
    FILE *file = fopen(filename, "w");
    if (!file) {
        fprintf(stderr, "无法创建文件 %s\n", filename);
        return;
    }

    for (int i = 0; i < size; i++) {
        uint32_t hex_value;
        memcpy(&hex_value, &data[i], sizeof(float));
        fprintf(file, "%08x\n", hex_value);
    }

    fclose(file);
}

int main() {
    // 分配矩阵内存
    float *src1 = (float *)malloc(M * N * sizeof(float));
    float *src2 = (float *)malloc(N * P * sizeof(float));
    float *src3 = (float *)malloc(M * P * sizeof(float));
    float *result = (float *)malloc(M * P * sizeof(float));

    if (!src1 || !src2 || !src3 || !result) {
        fprintf(stderr, "内存分配失败\n");
        return 1;
    }

    // 读取输入文件
    if (!read_hex_file("SRC1.txt", src1, M * N)) {
        free(src1); free(src2); free(src3); free(result);
        return 1;
    }
    if (!read_hex_file("SRC2.txt", src2, N * P)) {
        free(src1); free(src2); free(src3); free(result);
        return 1;
    }
    if (!read_hex_file("SRC3.txt", src3, M * P)) {
        free(src1); free(src2); free(src3); free(result);
        return 1;
    }

    // 执行矩阵乘法
    matrix_multiply(src1, src2, result, M, N, P);

    // 加上 SRC3
    matrix_add(result, src3, M, P);

    // 保存结果
    save_hex_file("output.txt", result, M * P);

    // 释放内存
    free(src1);
    free(src2);
    free(src3);
    free(result);

    return 0;
}