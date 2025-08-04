<script setup>
import { ref, onMounted } from 'vue';
import { sendemail } from '../api/event.ts'
import { useRoute } from 'vue-router'
import { getAllUser, getManagerList } from '../api/user.ts'
// import Markdown from '../components/Markdown.vue'
import EditEmail from '@/components/EditEmail.vue';
import { getFileList } from '@/api/file.js';
import { marked } from 'marked';
import DOMPurify from 'dompurify'
import { ElMessage } from 'element-plus';

const route = useRoute()

marked.setOptions({
  breaks: true, // 将回车转换为 <br>
  gfm: true, // 启用 GitHub 风格的 Markdown
  // sanitize: false, // 允许HTML标签
})

// 表单数据
const formData = ref({
  receiver: '',
  subject: '',
  content: '',
  store_upload_files: false
});

// 状态管理
const isSending = ref(false);
const message = ref(null);
const options = ref([])
const fileList = ref([])
const option = ref([{ label: '普通用户', value: 'isyourday' }, { label: '管理员', value: 'user' }])
const email_type = ref('isyourday')
const id_list = ref([])
const file_list = ref([])
const files_id = ref([])
const file_range = ref('private')
const content = ref('')
const type = ref(true)
const handleChange = (uploadFile, uploadFiles) => {
  fileList.value = uploadFiles

}

// 处理文件上传
const getUserList = async (type = 'isyourday') => {
  if (type === 'isyourday') {
    const res = await getAllUser()
    options.value = res.data.items.map((item) => {
      return {
        label: item.real_name,
        value: item.id
      }
    })
  }
  else {
    const res = await getManagerList()
    options.value = res.data.items.map((item) => {
      return {
        label: item.username,
        value: item.id
      }
    })
  }
}
const getFileRange = async () => {
  const ret = await getFileList(file_range.value)
  file_list.value = ret.data.items.map(item => {
    return {
      label: item.name,
      value: item.id
    }
  })
}

// 移除附件


// 发送邮件
const sendEmail = async () => {
  // 验证表单
  if (!id_list.value.length || !formData.value.subject) {
    showMessage('请填写所有必填字段', 'error');
    return;
  }
  isSending.value = true;
  message.value = null;

  formData.value.receiver = id_list.value.join(',')

  if(type.value){
    const text = DOMPurify.sanitize(marked(content.value))
    formData.value.content = text
  }
  else{
    formData.value.content = DOMPurify.sanitize(content.value)
  }
  
  formData.value.send_directly = true
  // formData.value.store_upload_files = true

  // const form = objectToFormData(formData.value)
  const form = new FormData()
  Object.entries(formData.value).forEach(([key, value]) => {
    form.append(key, value);
  });

  if (fileList.value.length > 0) {
    fileList.value.forEach(item => {
      form.append('files', item.raw)
    })
  }
  if (files_id.value.length > 0) {
    const str = files_id.value.join(',')
    form.append('files_in_store', str)
  }
  
  
  const res = await sendemail(email_type.value, form)
  if (res.status === 200) {
    ElMessage.success('邮件发送成功！')
  }
  resetForm()
  isSending.value = false
};

// 显示消息
const showMessage = (text, type) => {
  message.value = { text, type };
};

// 重置表单
const resetForm = () => {
  formData.value = {
    receiver: '',
    subject: '',
    content: '',
    store_upload_files: false
  };
  content.value = ''
  id_list.value = []
  files_id.value = []
};

onMounted(() => {
  getUserList()
  getFileRange()
})
</script>

<template>
  <div class="email-sender">
    <div class="header">
      <h2>发送邮件</h2>
    </div>
    <form @submit.prevent="sendEmail" class="email-form">
      <div class="form-group" style="display: flex;flex-direction: row;flex-wrap: wrap;">
        <label for="recipient" style="width: 100%;">收件人:</label>
        <el-select size="large" @change="getUserList(email_type)" v-model="email_type" placeholder="Select" style="width: 110px;">
          <el-option v-for="item in option" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        <el-select-v2 v-model="id_list" :options="options" size="large" placeholder="请选择收件人" style="flex: 1;" multiple
          filterable collapse-tags collapse-tags-tooltip :max-collapse-tags="3" :reserve-keyword="false" />
      </div>

      <div class="form-group">
        <label for="subject">主题:</label>
        <input type="text" id="subject" v-model="formData.subject" required placeholder="邮件主题" />
      </div>

      <div class="form-group">
        <label for="content">内容:<button type="button" @click="type=!type" style="float: right;height: 30px;padding: 0 10px;">html: {{ type?'已开启':'已关闭' }}</button></label>
        <!-- <textarea
          id="content"
          v-model="formData.content"
          required
          rows="8"
          placeholder="请输入邮件内容..."
        ></textarea> -->
        <!-- <Markdown /> -->
        <EditEmail :type="type" v-model="content" />
      </div>
      <div class="form-group">
        <label for="file">附件</label>
        <el-upload v-model:file-list="fileList" class="upload-demo" action="#" :on-change="handleChange"
          :auto-upload="false">
          <el-button type="primary">本地上传</el-button>
          <template #tip>
            <div class="el-upload__tip">
              jpg/png files with a size less than 500kb
            </div>
          </template>
        </el-upload>
      </div>
      <div class="form-group" style="display: flex;flex-direction: row;">
        <el-select @change="getFileRange" size="large" v-model="file_range" placeholder="Select" style="width: 110px;">
          <el-option key="public" label="public" value="public" />
          <el-option key="private" label="private" value="private" />
          <el-option key="global" label="global" value="global" />
          <el-option key="all" label="all" value="all" />
        </el-select>
        <el-select-v2 v-model="files_id" :options="file_list" size="large" placeholder="请选择文件" style="flex: 1;" multiple
          filterable collapse-tags collapse-tags-tooltip :max-collapse-tags="3" :reserve-keyword="false" />
      </div>

      <button type="submit" :disabled="isSending">
        {{ isSending ? '发送中...' : '发送邮件' }}
      </button>

      <div v-if="message" :class="['message', message.type]">
        {{ message.text }}
      </div>
    </form>
  </div>
</template>

<style scoped>
.email-sender {
  width: 100%;
  margin: 0 auto;
}

.email-form {
  display: flex;
  flex-direction: column;
  gap: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

/* select */

/* select */

label {
  font-weight: bold;
}

input[type="email"],
input[type="text"],
textarea {
  padding: 10px;
  border: 1px solid #ccc;
  border-radius: 4px;
  font-size: 16px;
  resize: none;
  outline: none;
}

input[type="email"]:focus,
input[type="text"]:focus,
textarea:focus {
  border-color: cornflowerblue;
}

textarea {
  resize: none;
}

button {
  padding: 12px 20px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
  transition: background-color 0.3s;
}

button:hover:not(:disabled) {
  background-color: #45a049;
}

button:disabled {
  background-color: #cccccc;
  cursor: not-allowed;
}

.attachments-preview {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 8px;
}

.attachment-item {
  display: flex;
  align-items: center;
  gap: 5px;
  padding: 5px 10px;
  background-color: #f0f0f0;
  border-radius: 4px;
}

.attachment-item button {
  padding: 2px 6px;
  background-color: #ff4444;
  font-size: 12px;
}

.attachment-item button:hover {
  background-color: #cc0000;
}

.message {
  padding: 10px;
  border-radius: 4px;
  margin-top: 15px;
}

.message.success {
  background-color: #dff0d8;
  color: #3c763d;
}

.message.error {
  background-color: #f2dede;
  color: #a94442;
}
</style>