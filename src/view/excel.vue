<template>
  <el-card class="full-screen-card">
    <div class="container p-4 font-inter">
      <div class="max-w-4xl w-full bg-white rounded-xl shadow-lg p-6 border border-gray-100">
        <!-- 标题放在左上角 -->
        <div class="mb-8">
          <h1 class="text-[clamp(1.5rem,3vw,2.5rem)] font-bold text-gray-800 mb-2">Excel 数据上传</h1>
          <p class="text-gray-500">请上传员工信息Excel文件，系统将自动解析并导入数据</p>
        </div>

        <!-- 放大的文件上传框，占页面上半部分 -->
        <div class="mb-8 upload-container">
          <el-upload
            ref="uploadRef"
            class="upload-demo"
            drag
            :action="uploadUrl"
            :on-change="handleFileChange"
            :before-upload="beforeUpload"
            :auto-upload="false"
            accept=".xlsx"
            multiple
          >
            <el-icon class="el-icon--upload" style="font-size: 64px; margin-bottom: 24px;">
              <upload-filled />
            </el-icon>
            <div class="el-upload__text">
              拖拽文件到此处上传或 <em>点击选择文件</em>
            </div>
            <div class="el-upload__tip" style="margin-top: 16px; font-size: 16px;">
              支持单个或多个.xlsx文件
            </div>
          </el-upload>
          
          <div class="mt-6 flex justify-between items-center">
            <div class="text-base text-gray-500">
              <span class="text-primary">*</span> 仅支持 .xlsx 格式文件
            </div>
            <el-button type="link" @click="showTemplateDialog">
              <i class="fa fa-table mr-1"></i> 查看xlsx格式
            </el-button>
          </div>
        </div>

        <!-- 放大的已选择文件区域 -->
        <div v-if="selectedFiles.length > 0" class="mb-8 selected-files-container">
          <h3 class="font-semibold text-gray-700 mb-4 text-lg">已选择的文件</h3>
          <el-table :data="selectedFiles" stripe style="width: 100%; font-size: 15px;">
            <el-table-column prop="name" label="文件名" min-width="300"></el-table-column>
            <el-table-column prop="size" label="大小" min-width="120" :formatter="formatSize"></el-table-column>
            <el-table-column label="操作" min-width="120">
              <template #default="scope">
                <el-button size="mini" type="danger" @click="removeFile(scope.$index)">
                  <i class="fa fa-trash-o"></i>
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="flex justify-center mt-8">
          <el-button
            :loading="isLoading"
            type="primary"
            size="large"
            :disabled="selectedFiles.length === 0"
            @click="parseAndSend"
          >
            <i class="fa fa-paper-plane mr-2"></i> 解析并发送
          </el-button>
        </div>

        <!-- 模板格式对话框 -->
        <el-dialog v-model="templateDialogVisible" title="Excel模板格式">
          <div class="p-4">
            <p class="mb-4">请确保Excel文件包含以下列标题，且顺序可任意：</p>
            <el-table :data="templateColumns" stripe style="width: 100%">
              <el-table-column prop="field" label="字段名" min-width="150"></el-table-column>
              <el-table-column prop="description" label="描述" min-width="250"></el-table-column>
              <el-table-column prop="example" label="示例" min-width="150"></el-table-column>
            </el-table>
            <div class="mt-4 p-3 bg-gray-50 rounded">
              <p class="text-sm text-gray-600"><i class="fa fa-info-circle text-primary mr-1"></i> 性别编码说明：女=1，男=2，未知=0</p>
              <p class="text-sm text-gray-600 mt-1"><i class="fa fa-info-circle text-primary mr-1"></i> 日期格式要求：YYYY-MM-DD</p>
            </div>
          </div>
          <template #footer>
            <span class="dialog-footer">
              <el-button @click="templateDialogVisible = false">取消</el-button>
              <el-button type="primary" @click="downloadTemplate">
                <i class="fa fa-download mr-1"></i> 下载模板
              </el-button>
            </span>
          </template>
        </el-dialog>

        <!-- 结果对话框 -->
        <el-dialog v-model="resultDialogVisible" :title="resultDialogTitle" width="30%">
          <div class="p-4">
            <div v-if="batchResult.totalCount > 0">
              <p class="mb-3 text-center font-medium">处理结果：</p>
              <div class="flex flex-col space-y-2">
                <div class="flex justify-between">
                  <span>成功：</span>
                  <span class="text-green-500 font-medium">{{ batchResult.successCount }}</span>
                </div>
                <div class="flex justify-between">
                  <span>失败：</span>
                  <span class="text-red-500 font-medium">{{ batchResult.failedCount }}</span>
                </div>
                <div class="flex justify-between border-t border-gray-200 pt-2 mt-2">
                  <span class="font-medium">总计：</span>
                  <span class="font-medium">{{ batchResult.totalCount }}</span>
                </div>
              </div>
              <div v-if="batchResult.failedCount > 0" class="mt-4 text-center">
                <el-button size="small" type="primary" @click="showErrorDetails">
                  <i class="fa fa-list mr-1"></i> 查看失败详情
                </el-button>
              </div>
            </div>
            <div v-else>
              <p class="text-center">{{ resultDialogMessage }}</p>
            </div>
          </div>
          <template #footer>
            <el-button type="primary" @click="resultDialogVisible = false">确定</el-button>
          </template>
        </el-dialog>

        <!-- 错误详情对话框 -->
        <el-dialog v-model="errorDialogVisible" title="失败详情">
          <div class="p-4">
            <el-table :data="errorDetails" stripe style="width: 100%">
              <el-table-column prop="rowIndex" label="行号" width="80"></el-table-column>
              <el-table-column prop="errorMsg" label="错误信息"></el-table-column>
            </el-table>
          </div>
          <template #footer>
            <el-button @click="errorDialogVisible = false">关闭</el-button>
          </template>
        </el-dialog>
      </div>
    </div>
  </el-card>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { read, utils, writeFile } from 'xlsx'
import axios from 'axios'
import { UploadFilled } from '@element-plus/icons-vue'
import { ApiBaseURL } from '@/utils/request'

// 组件状态
const uploadRef = ref(null)
const selectedFiles = ref([])
const isLoading = ref(false)
const templateDialogVisible = ref(false)
const errorDialogVisible = ref(false)
const resultDialogVisible = ref(false)
const errorDetails = ref([])

// 结果对话框内容
const resultDialogTitle = ref('')
const resultDialogMessage = ref('')

// API配置
const baseUrl = ApiBaseURL
const uploadUrl = `${ApiBaseURL}/isyourday/user`
// const token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhYTlkMWQwMi0wZTc0LTQ1MzQtOTk0ZS00MzY1NjBiNGI4ZGQiLCJzY29wZXMiOlsiYXV0aDpyZWFkX2Jhc2ljIiwiYXV0aDpyZWFkX2FsbCIsImF1dGg6d3JpdGUiLCJhdXRoOmRlbGV0ZSIsImZpbGU6cmVhZCIsImZpbGU6dXBsb2FkIiwiZmlsZTp3cml0ZSIsImZpbGU6ZGVsZXRlIiwiaXN5b3VyZGF5OnJlYWQiLCJpc3lvdXJkYXk6d3JpdGUiLCJpc3lvdXJkYXk6ZGVsZXRlIl0sImV4cCI6MTc1Mzg1OTM0OH0.jSkyFR1uB7mWdC17OwA99ZQHx-duW_yfxeEv-fxVl7o'
const token = localStorage.getItem('access_token')

// Excel模板配置
const templateColumns = [
  { field: 'real_name', description: '姓名', example: '张三' },
  { field: 'sex', description: '性别(0=未知,1=女,2=男)', example: '2' },
  { field: 'birthday', description: '出生日期(YYYY-MM-DD)', example: '1990-01-01' },
  { field: 'tel', description: '电话号码', example: '13800138000' },
  { field: 'prompt', description: '备注信息', example: '技术部员工' },
  { field: 'location', description: '地址', example: '北京市朝阳区' },
  { field: 'QQ', description: 'QQ号码', example: '12345678' },
  { field: 'wechat', description: '微信号', example: 'zhangsan' },
  { field: 'identify', description: '身份证号', example: '110101199001011234' },
  { field: 'email', description: '邮箱', example: 'zhangsan@example.com' }
]

// 批量处理结果
const batchResult = reactive({
  successCount: 0,
  failedCount: 0,
  totalCount: 0,
  errors: []
})

// 文件大小格式化
const formatSize = (row) => {
  const size = row.size
  if (size < 1024) return size + 'B'
  else if (size < 1024 * 1024) return (size / 1024).toFixed(2) + 'KB'
  else return (size / (1024 * 1024)).toFixed(2) + 'MB'
}

// 文件变更处理
const handleFileChange = (file, fileList) => {
  selectedFiles.value = fileList
}

// 上传前验证
const beforeUpload = (file) => {
  const extension = file.name.split('.').pop().toLowerCase()
  if (extension !== 'xlsx') {
    ElMessage.error('请上传.xlsx格式的文件')
    return false
  }
  return true
}

// 移除文件
const removeFile = (index) => {
  selectedFiles.value.splice(index, 1)
}

// 显示模板对话框
const showTemplateDialog = () => {
  templateDialogVisible.value = true
}

// 解析并发送数据
const parseAndSend = async () => {
  if (selectedFiles.value.length === 0) {
    ElMessage.warning('请先选择文件')
    return
  }

  if (!token) {
    ElMessage.error('缺少身份验证令牌，请重新登录')
    return
  }

  // 重置结果
  Object.assign(batchResult, {
    successCount: 0,
    failedCount: 0,
    totalCount: 0,
    errors: []
  })
  
  isLoading.value = true
  
  try {
    for (const file of selectedFiles.value) {
      await processFile(file)
    }
    
    resultDialogTitle.value = '处理完成'
    resultDialogVisible.value = true
  } catch (error) {
    resultDialogTitle.value = '处理失败'
    resultDialogMessage.value = error.message || '未知错误'
    resultDialogVisible.value = true
  } finally {
    isLoading.value = false
  }
}

// 处理单个文件
const processFile = async (file) => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    
    reader.onload = async (e) => {
      try {
        const data = new Uint8Array(e.target.result)
        const workbook = read(data, { type: 'array' })
        
        // 获取第一个工作表
        const firstSheetName = workbook.SheetNames[0]
        const worksheet = workbook.Sheets[firstSheetName]
        
        // 转换为JSON并打印解析结果
        const jsonData = utils.sheet_to_json(worksheet)

        
        if (jsonData.length === 0) {
          throw new Error('Excel文件中没有数据')
        }
        
        // 处理数据并发送
        await processAndSendData(jsonData)
        resolve()
      } catch (error) {
        console.error('处理文件时出错:', error)
        reject(error)
      }
    }
    
    reader.onerror = () => {
      reject(new Error('文件读取失败'))
    }
    
    reader.readAsArrayBuffer(file.raw)
  })
}

// 处理数据并发送到API
const processAndSendData = async (data) => {
  const results = {
    successCount: 0,
    failedCount: 0,
    totalCount: data.length,
    errors: []
  }
  
  // 批量处理，每100条记录一批
  const batchSize = 100
  for (let i = 0; i < data.length; i += batchSize) {
    const batch = data.slice(i, i + batchSize)
    const processedBatch = batch.map((row, index) => {
      try {
        return processRow(row, i + index + 2)
      } catch (error) {
        results.failedCount++
        results.errors.push({
          rowIndex: i + index + 2,
          errorMsg: error.message
        })
        return null
      }
    }).filter(item => item !== null)
    
    if (processedBatch.length > 0) {
      try {
        await sendDataToApi(processedBatch)
        results.successCount += processedBatch.length
      } catch (error) {
        const errorMsg = error.response?.data?.message || 'API请求失败'
        
        if (error.response && error.response.status === 401) {
          ElMessage.error('身份验证失败，请重新登录')
        }
        
        processedBatch.forEach((_, index) => {
          results.failedCount++
          results.errors.push({
            rowIndex: i + index + 2,
            errorMsg: errorMsg
          })
        })
      }
    }
  }
  
  // 更新总结果
  batchResult.successCount += results.successCount
  batchResult.failedCount += results.failedCount
  batchResult.totalCount += results.totalCount
  batchResult.errors.push(...results.errors)
}

// 处理单行数据
const processRow = (row, rowIndex) => {
  if (!row.real_name) {
    throw new Error('缺少姓名')
  }
  
  let sex = parseInt(row.sex)
  if (isNaN(sex) || ![0, 1, 2].includes(sex)) {
    sex = 0
  }
  
  let birthday = row.birthday
  if (birthday) {
    if (typeof birthday === 'number') {
      const date = new Date((birthday - 25569) * 86400 * 1000)
      birthday = date.toISOString()
    } else if (typeof birthday === 'string') {
      const date = new Date(birthday)
      if (!isNaN(date.getTime())) {
        birthday = date.toISOString()
      } else {
        console.warn(`第 ${rowIndex} 行的出生日期格式无效:`, birthday)
        birthday = ''
      }
    }
  } else {
    birthday = ''
  }
  
  return {
    real_name: row.real_name || '',
    sex: sex,
    birthday: birthday,
    tel: row.tel || '',
    prompt: row.prompt || '',
    location: row.location || '',
    QQ: row.QQ || '',
    wechat: row.wechat || '',
    identify: row.identify || '',
    email: row.email || ''
  }
}

// 发送数据到API
const sendDataToApi = async (data) => {
  try {
    const response = await axios.post(uploadUrl, data, {
      headers: {
        'accept': 'application/json',
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`
      }
    })
    
    if (response.status !== 200 && response.status !== 201) {
      throw new Error(`API返回错误状态码: ${response.status}`)
    }
    
    return response.data
  } catch (error) {
    console.error('API请求错误:', error)
    if (error.response) {
      console.error('错误响应状态:', error.response.status)
      console.error('错误响应数据:', error.response.data)
    }
    throw error
  }
}

// 显示错误详情
const showErrorDetails = () => {
  errorDetails.value = batchResult.errors
  errorDialogVisible.value = true
}

// 下载模板
const downloadTemplate = () => {
  const wb = utils.book_new()
  const header = templateColumns.map(col => col.field)
  const ws_data = [header]
  const ws = utils.aoa_to_sheet(ws_data)
  utils.book_append_sheet(wb, ws, "模板")
  writeFile(wb, "员工信息模板.xlsx")
}
</script>

<style scoped>
.full-screen-card {
  width: 97.1%;
  height: 105vh;
  border-radius: 0;
  overflow: auto;
  padding: 20px;
}

.container {
  justify-content: center; /* 水平居中 */
  width: 100%;
  min-height: 100%;
  background-color: #f8fafc;
}

/* 上传区域样式 - 放大并占上半部分 */
.upload-container {
  justify-content: center; /* 水平居中 */
  width: 100%;
  height:40%;
  margin-bottom: 30px;
}

.upload-demo {
  width: 100%;
  min-height: 350px; /* 增大上传框高度 */
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.el-upload-dragger {
  width: 100% !important;
  height: 350px !important; /* 上传拖拽区域高度 */
  display: flex !important;
  flex-direction: column !important;
  justify-content: center !important;
  padding: 40px 20px !important;
  border-width: 3px !important;
  border-style: dashed !important;
}

/* 已选择文件区域样式 - 拉大并增强视觉效果 */
.selected-files-container {
  width: 95%;
  padding: 20px;
  background-color: #fafafa;
  border-radius: 8px;
  border: 1px solid #eee;
}

.el-table {
  margin-top: 16px;
  font-size: 15px;
}

.el-table th {
  padding: 15px 0 !important;
  font-size: 15px !important;
}

.el-table td {
  padding: 15px 0 !important;
}

/* 按钮和文本样式调整 */
.el-button {
  transition: all 0.3s ease;
  font-size: 15px !important;
  padding: 10px 20px !important;
}

.el-button:hover:not(.is-disabled) {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
}

.el-icon--upload {
  color: #8c939b;
}

.el-upload__text {
  font-size: 18px;
  color: #606266;
  margin-bottom: 16px;
}

.el-upload__text em {
  color: #409eff;
  font-style: normal;
  font-weight: 500;
}

.el-upload__tip {
  font-size: 14px;
  color: #909399;
}

/* 对话框样式保持不变 */
.el-dialog {
  border-radius: 12px;
  overflow: hidden;
}

.el-dialog__header {
  background-color: #f5f7fa;
  border-bottom: 1px solid #ebeef5;
}
</style>