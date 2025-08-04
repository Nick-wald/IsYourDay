<script setup>
import { ref, computed, onMounted } from 'vue';
import { getEmailHistory, updateEmailHistory, sendPendingEmail } from '@/api/event';
import { searchManager } from '@/api/user';
import dayjs from 'dayjs';
import { ApiBaseURL } from '@/utils/request';
import { fileDetail } from '@/api/file';
import EditEmail from '@/components/EditEmail.vue';
import { ElMessage } from 'element-plus';

const page_num = ref(0);
const total = ref(0);
const search_type = ref('receiver_name_search');
const mockRecords = ref([]);
const searchQuery = ref('');
const showModal = ref(false);
const currentRecord = ref({});
const isEditing = ref(false);
const editedContent = ref({
  content: '',
  subject: '',
});

// 计算属性
const showEditButton = computed(() => {
  return ['pending', 'failed'].includes(currentRecord.value?.status);
});

const statusClass = computed(() => {
  return {
    'failed': ['pending', 'failed'].includes(currentRecord.value?.status),
    'success': currentRecord.value?.status === 'success'
  };
});

const hasAttachments = computed(() => {
  return currentRecord.value?.attachments?.length > 0;
});

const sendEmail = async (id) => {
  try {
    await sendPendingEmail(id)
    getList()
    ElMessage.success('邮件发送成功')
  } catch(error) {
  }
  
}

// 获取邮件历史记录
const getList = async (num = 0) => {
  page_num.value = num;
  const data = {
    skip: num * 10,
    limit: 10,
    global_search: true,
  };
  
  if (searchQuery.value) {
    data.q = searchQuery.value;
  }
  
  const res = await getEmailHistory(search_type.value, data);
  total.value = res.data.pagination.total_pages;

  mockRecords.value = await Promise.all(res.data.items.map(async (item) => {
    const sender = await searchManager('id', item.sender_id);
    const files_id = item.attachments.split(',').filter(Boolean);
    const files = files_id.map((fileId) => {
      // const res = await fileDetail(fileId)
      return {
        id: fileId,
        name: fileId, // 这里应该是文件名，可能需要从API获取
        url: `${ApiBaseURL}/file/${fileId}/download`,
        // size: res.data.size // 可能需要从API获取文件大小
      };
    });

    return {
      receiver_emails: item.receiver_emails.split(',').filter(Boolean),
      receiver_type: item.receiver_type,
      sender: sender.data,
      content: item.content,
      sent_at: dayjs(item.sent_at).format('YYYY-MM-DD HH:mm:ss'),
      id: item.id,
      receiver_names: item.receiver_names.split(',').filter(Boolean),
      subject: item.subject,
      attachments: files,
      status: item.status,
      reason: item.reason
    };
  }));
  
};

onMounted(() => {
  getList();
});

// 显示详情
const showDetail = (record) => {

  
  currentRecord.value = { ...record };
  showModal.value = true;
  isEditing.value = false;
};

// 关闭模态框
const closeModal = () => {
  showModal.value = false;
};

// 启用编辑
const enableEditing = () => {
  isEditing.value = true;
  editedContent.value.content = currentRecord.value.content;
  editedContent.value.subject = currentRecord.value.subject;
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
};

// 保存更改
const saveChanges = async () => {
  const files = currentRecord.value.attachments.map(item => {
    return item.id
  })
  const form = new FormData()
  const data = {
    ...editedContent.value,
    receiver_type: currentRecord.value.receiver_type,
    receiver_emails: currentRecord.value.receiver_emails.join(','),
    receiver_names: currentRecord.value.receiver_names.join(','),
    attachments: files.join(',')
  }
  Object.entries(data).forEach(([key, value]) => {
    form.append(key, value);
  });
  // if(files.length > 0) {
  //   form.append('attachments', files.join(','))
  // }
  // const res = await updateEmailHistory(currentRecord.value.id,data)
  try {
    // 这里应该调用API更新邮件内容
    // await updateEmailContent(currentRecord.value.id, editedContent.value);
    await updateEmailHistory(currentRecord.value.id, data)
    // 更新本地数据
    currentRecord.value.subject = editedContent.value.subject
    currentRecord.value.content = editedContent.value.content;
    currentRecord.value.status = 'pending'; // 更新状态为pending
    isEditing.value = false;
    
    getList()
    // 更新列表中的对应记录
    // const index = mockRecords.value.findIndex(r => r.id === currentRecord.value.id);
    // if (index !== -1) {
    //   mockRecords.value[index] = { ...currentRecord.value };
    // }
  } catch (error) {
    console.error('保存失败:', error);
  }
};

// 文件图标
const getFileIcon = (filename) => {
  const ext = filename.split('.').pop().toLowerCase();
  const icons = {
    pdf: '📄',
    doc: '📝',
    docx: '📝',
    xls: '📊',
    xlsx: '📊',
    ppt: '📑',
    pptx: '📑',
    jpg: '🖼️',
    png: '🖼️',
    gif: '🖼️',
    zip: '🗄️',
    rar: '🗄️',
    txt: '📋'
  };
  return icons[ext] || '📎';
};

// 格式化文件大小
const formatFileSize = (bytes) => {
  if (bytes === 0) return '0 Bytes';
  const k = 1024;
  const sizes = ['Bytes', 'KB', 'MB', 'GB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
};

// 下载附件
const downloadAttachment = (file) => {
  window.open(file.url, '_blank');
};
</script>

<template>
  <div class="mail-history-container">
    <h1>邮件发送历史记录</h1>

    <div class="search-bar">
      <input v-model="searchQuery" placeholder="搜索收件人" class="search-input" />
      <button @click="getList(page_num)" class="refresh-btn">
        <span class="icon">↻</span> 刷新
      </button>
    </div>

    <div class="history-list">
      <div v-for="record in mockRecords" :key="record.id" @click="showDetail(record)" class="history-item">
        <div class="item-header">
          <span class="subject">{{ record.subject }}</span>
          <span class="date">{{ record.sent_at }}</span>
        </div>
        <div class="item-content">
          <span class="recipient">收件人: {{ record.receiver_names.join(',') }}</span>
          <span class="status" :class="record.status">{{ record.status }}</span>
        </div>
      </div>

      <div v-if="mockRecords.length === 0" class="empty-tip">
        没有找到匹配的邮件记录
      </div>
    </div>

    <div class="pagination-container">
      <div class="pagination">
        <button @click="getList(--page_num)" class="page-btn prev-btn" :disabled="page_num == 0">上一页</button>
        <div class="page-numbers">
          {{ page_num + 1 }}
        </div>
        <button @click="getList(++page_num)" class="page-btn next-btn"
          :disabled="page_num + 1 >= total">下一页</button>
      </div>
    </div>

    <!-- 详情弹窗 -->
    <div v-if="showModal" class="modal-overlay" @click.self="closeModal">
      <div class="modal-content">
        <button class="close-btn" @click="closeModal">×</button>
        <h2 v-show="!isEditing">{{ currentRecord.subject }}</h2>
        <input style="width: 80%;height: 30px;" v-show="isEditing" v-model="editedContent.subject" type="text">

        <div class="detail-section">
          <div class="detail-row">
            <span class="detail-label">发送时间:</span>
            <span class="detail-value">{{ currentRecord.sent_at }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">发件人:</span>
            <span class="detail-value">{{ currentRecord.sender.username }}<{{ currentRecord.sender.email }}></span>
          </div>
          <div class="detail-row">
            <span class="detail-label">收件人:</span>
            <span class="detail-value">{{ currentRecord.receiver_names.join(',') }}</span>
          </div>
          <div class="detail-row">
            <span class="detail-label">状态:</span>
            <span class="detail-value" :class="statusClass">
              {{ currentRecord.status }}
            </span>
          </div>
          <div class="detail-row" v-show="currentRecord.status === 'failed'">
            <span class="detail-label">原因:</span>
            <span class="detail-value">
              {{ currentRecord.reason }}
            </span>
          </div>
        </div>

        <div class="content-section">
          <div class="section-header">
            <h3>邮件内容</h3>
            <div style="flex: 1;"></div>
            <button 
              v-if="showEditButton" 
              @click="enableEditing" 
              class="edit-btn"
              :disabled="isEditing"
              style="margin-right: 5px;"
            >
              编辑
            </button>
            <button 
              v-if="showEditButton" 
              @click="sendEmail(currentRecord.id)" 
              class="edit-btn"
              :disabled="isEditing"
              style="background-color: hsl(113, 51%, 52%);"
            >
              发送
            </button>
          </div>

          <div v-if="!isEditing" class="email-content" v-html="currentRecord.content"></div>

          <!-- 编辑区域 -->
          <div v-if="isEditing" class="edit-section">
            <!-- <textarea 
              v-model="editedContent.content" 
              class="content-editor" 
              placeholder="请输入邮件内容..."
            ></textarea> -->

            <EditEmail :type="false" v-model="editedContent.content" />
            
            <div class="edit-actions">
              <button @click="saveChanges" class="save-btn">保存更改</button>
              <button @click="cancelEditing" class="cancel-btn">取消</button>
            </div>
          </div>
        </div>

        <div v-if="hasAttachments" class="attachment-section">
          <h3>附件 ({{ currentRecord.attachments.length }})</h3>
          <div class="attachment-list">
            <div 
              v-for="(file, index) in currentRecord.attachments" 
              :key="index" 
              class="attachment-item"
            >
              <span class="file-icon">{{ getFileIcon(file.name) }}</span>
              <span class="file-name">{{ file.name }}</span>
              <!-- <span class="file-size">({{ formatFileSize(file.size) }})</span> -->
              <button @click.stop="downloadAttachment(file)" class="download-btn">下载</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>



<style scoped>

.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 15px;
}

.edit-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  padding: 8px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.3s;
  font-size: 14px;
}

.edit-btn:hover:not(:disabled) {
  background-color: #66b1ff;
}

.edit-btn:disabled {
  opacity: 0.6;
  cursor: not-allowed;
}

.edit-section {
  margin-top: 15px;
  border: 1px solid #eaeaea;
  border-radius: 4px;
  padding: 15px;
  background-color: #f9f9f9;
}

.content-editor {
  width: 100%;
  min-height: 200px;
  padding: 10px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  resize: vertical;
  font-family: inherit;
  font-size: 14px;
  line-height: 1.5;
}

.content-editor:focus {
  outline: none;
  border-color: #409EFF;
  box-shadow: 0 0 0 2px rgba(64, 158, 255, 0.2);
}

.edit-actions {
  margin-top: 15px;
  text-align: right;
}

.save-btn, .cancel-btn {
  padding: 8px 20px;
  border-radius: 4px;
  cursor: pointer;
  border: none;
  margin-left: 10px;
  transition: all 0.3s;
  font-size: 14px;
}

.save-btn {
  background-color: #67C23A;
  color: white;
}

.save-btn:hover {
  background-color: #85ce61;
}

.cancel-btn {
  background-color: #F56C6C;
  color: white;
}

.cancel-btn:hover {
  background-color: #f78989;
}

.failed {
  color: #F56C6C;
}

.success {
  color: #67C23A;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .edit-actions {
    display: flex;
    flex-direction: column;
    gap: 10px;
  }
  
  .save-btn, .cancel-btn {
    width: 100%;
    margin-left: 0;
  }
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.edit-btn {
  background-color: #409EFF;
  color: white;
  border: none;
  padding: 5px 10px;
  border-radius: 4px;
  cursor: pointer;
}

.edit-section {
  margin-top: 15px;
}

.content-editor {
  width: 100%;
  min-height: 200px;
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  resize: vertical;
}

.edit-actions {
  margin-top: 10px;
  text-align: right;
}

.save-btn {
  background-color: #67C23A;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 4px;
  margin-right: 10px;
  cursor: pointer;
}

.cancel-btn {
  background-color: #F56C6C;
  color: white;
  border: none;
  padding: 5px 15px;
  border-radius: 4px;
  cursor: pointer;
}

/* 分页样式 */
.pagination-container {
  display: flex;
  justify-content: center;
  margin-top: 20px;
}

.pagination {
  display: flex;
  align-items: center;
}

.page-btn {
  padding: 8px 15px;
  margin: 0 5px;
  border: 1px solid #d9d9d9;
  background-color: #fff;
  border-radius: 4px;
  cursor: pointer;
}

.page-btn:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

.page-btn:hover:not(:disabled) {
  color: #1890ff;
  border-color: #1890ff;
}

.page-numbers {
  padding: 8px 15px;
  margin: 0 5px;
}

/* ==== */

.mail-history-container {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  font-family: 'Arial', sans-serif;
}

h1 {
  color: #333;
  margin-bottom: 20px;
}

.search-bar {
  display: flex;
  gap: 10px;
  margin-bottom: 20px;
}

.search-input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 16px;
}

.refresh-btn {
  padding: 10px 15px;
  background-color: #4CAF50;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 16px;
}

.refresh-btn:hover {
  background-color: #45a049;
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 10px;
}

.history-item {
  background-color: #fff;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding: 15px;
  cursor: pointer;
  transition: all 0.2s;
}

.history-item:hover {
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  transform: translateY(-2px);
}

.item-header {
  display: flex;
  justify-content: space-between;
  margin-bottom: 10px;
}

.subject {
  font-weight: bold;
  font-size: 18px;
  color: #333;
}

.date {
  color: #666;
  font-size: 14px;
}

.item-content {
  display: flex;
  justify-content: space-between;
}

.recipient {
  color: #555;
  font-size: 14px;
}

.status {
  padding: 3px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: bold;
}

.status.sent {
  background-color: #d4edda;
  color: #155724;
}

.status.pending {
  background-color: hsl(45, 70%, 91%);
  color: hwb(34 26% 31%);
}

.status.failed {
  background-color: #f8d7da;
  color: #721c24;
}

.empty-tip {
  text-align: center;
  padding: 30px;
  color: #666;
  font-size: 16px;
}

/* 弹窗样式 */
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: rgba(0, 0, 0, 0.5);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 1000;
}

.modal-content {
  background-color: #fff;
  border-radius: 8px;
  width: 80%;
  max-width: 800px;
  max-height: 90vh;
  overflow-y: auto;
  padding: 25px;
  position: relative;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.15);
}

.close-btn {
  position: absolute;
  top: 15px;
  right: 15px;
  background: none;
  border: none;
  font-size: 24px;
  cursor: pointer;
  color: #666;
}

.close-btn:hover {
  color: #333;
}

.detail-section {
  margin: 20px 0;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
}

.detail-row {
  display: flex;
  margin-bottom: 8px;
}

.detail-label {
  width: 80px;
  font-weight: bold;
  color: #555;
}

.detail-value {
  flex: 1;
}

.content-section {
  margin: 20px 0;
}

.email-content {
  margin-top: 10px;
  padding: 15px;
  background-color: #f9f9f9;
  border-radius: 4px;
  border-left: 3px solid #4CAF50;
}

.attachment-section {
  margin-top: 20px;
}

.attachment-list {
  margin-top: 10px;
}

.attachment-item {
  display: flex;
  align-items: center;
  padding: 10px;
  background-color: #f5f5f5;
  border-radius: 4px;
  margin-bottom: 8px;
}

.file-icon {
  margin-right: 10px;
  font-size: 20px;
}

.file-name {
  flex: 1;
  margin-right: 10px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-size {
  color: #666;
  margin-right: 10px;
  font-size: 14px;
}

.download-btn {
  padding: 5px 10px;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
}

.download-btn:hover {
  background-color: #0b7dda;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .modal-content {
    width: 95%;
    padding: 15px;
  }

  .detail-row {
    flex-direction: column;
  }

  .detail-label {
    width: auto;
    margin-bottom: 2px;
  }

  .item-header {
    flex-direction: column;
    gap: 5px;
  }

  .item-content {
    flex-direction: column;
    gap: 5px;
  }

  .attachment-item {
    flex-wrap: wrap;
    gap: 5px;
  }

  .file-name {
    flex: 0 0 100%;
    white-space: normal;
  }
}

@media (max-width: 480px) {
  .search-bar {
    flex-direction: column;
  }

  .refresh-btn {
    width: 100%;
  }
}
</style>