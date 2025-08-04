<script setup>
import { ref, onMounted } from 'vue'
import { getUserEvent, addEventOrMsg, delEventOrMsg, updateEventOrMsg } from '../api/event.ts'
import dayjs from 'dayjs'
import { useRoute } from 'vue-router'
import { getAllUser } from '../api/user'
import { UploadFilled } from '@element-plus/icons-vue'

// 响应式数据
const user_pk = ref('')
const event_pk = ref('')
const events = ref([])
const event = ref({
  pk: '',
  create_time: '',
  event_time: '',
  message: '',
  event_title: ''
})
const showCard = ref(false)
const cover = ref(false)
const is_add = ref(false)
const options = ref([])
const docCard = ref(false)
const route = useRoute()

const delMode = ref(false)
const isIndeterminate = ref(true)
const checkedEvents = ref([])
const checkAll = ref(false)
// 方法

const handleCheckAllChange = (val) => {
  const events_id = events.value.map((item) => {
    return item.id
  })
  checkedEvents.value = val ? events_id : []
  
  isIndeterminate.value = false
}

const handleCheckedEventChange = (value) => {
  const users = events.value.map((item) => {
    return item.id
  })
  const checkedCount = value.length
  checkAll.value = checkedCount === users.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < users.length
}

const getList = async () => {
  const res = await getAllUser()

  options.value = res.data.items.map(item => {
    return {
      label: item.real_name,
      value: item.id
    }
  })
}

const handleSearch = async (type = false) => {


  const res = await getUserEvent(user_pk.value)


  if (res.status === 200 && type) {
    ElMessage.success('用户事件获取成功')
  }
  events.value = res.data.items
}



const showAdd = () => {
  event.value = {
    start_time: '',
    end_time: '',
    description: '',
    title: '',
    prompt: ''
  }
  is_add.value = true
  showCard.value = true
  cover.value = true
}

const showEdit = (data) => {
  is_add.value = false
  event.value = { ...data }
  showCard.value = true
  cover.value = true
  event_pk.value = data.id
}

const hiddenCard = () => {
  showCard.value = false
  cover.value = false
}

const handleCreate = async () => {
  // 新建逻辑
  event.value.start_time = new Date(event.value.start_time).toISOString()
  event.value.end_time = new Date(event.value.end_time).toISOString()
  const formData = new FormData()
  Object.entries(event.value).forEach(([key, value]) => {
    formData.append(key, value);
  });

  const res = await addEventOrMsg(user_pk.value, formData)
  if (res.status >= 200 && res.status < 300) {
    ElMessage.success('事件新建成功')
  }
  showCard.value = false
  cover.value = false
  handleSearch()
}

const handleEdit = async () => {
  // 编辑逻辑
  const data = {
    ...event.value,
  }
  data.start_time = new Date(data.start_time).toISOString()
  data.end_time = new Date(data.end_time).toISOString()
  const res = await updateEventOrMsg(user_pk.value, data.id, data)
  if (res.status === 200) {
    ElMessage.success('事件修改成功')
  }
  showCard.value = false
  cover.value = false
  handleSearch()
}

const handleDelete = async () => {
  // 删除逻辑
  
  const res = await delEventOrMsg(user_pk.value, checkedEvents.value)
  if (res.status === 200) {
    ElMessage.success('事件删除成功')
  }
  handleSearch()
}

const deleteOneEvent = async (item) => {
  const list = [item.id]
  const res = await delEventOrMsg(user_pk.value, list)
  if (res.status === 200) {
    ElMessage.success('事件删除成功')
  }
  handleSearch()
}

const showDocCard = () => {
  docCard.value = true
}

const hiddenDocCard = () => {
  docCard.value = false
}

onMounted(() => {
  getList()
  if (route.query.pk) {
    user_pk.value = route.query.pk
    handleSearch(true)
  }

})
</script>

<template>
  <div class="main-content">
    <div class="header">
      <h2>事件管理</h2>
    </div>
    <div class="event-management">
      <!-- 操作栏 -->
      <div class="action-bar">
        <div class="search-box">
          <el-select @change="handleSearch" filterable v-model="user_pk" size="large" placeholder="请选择需要查询的用户" style="width: 100%;">
            <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
          </el-select>
        </div>
        <div class="action-buttons">
          <!-- <button class="btn-primary" @click="handleSearch">
            查询
          </button> -->
          <button class="btn-primary" @click="showAdd">
            <span class="icon">+</span> 新建事件
          </button>
          <!-- <button class="btn-primary" @click="showDocCard">
            <span class="icon">+</span> 批量导入
          </button> -->
          <button v-show="!delMode" @click="delMode = true" class="btn btn-primary">批量删除</button>
          <button class="btn btn-danger" @click="handleDelete" v-show="delMode">删除</button>
          <button class="btn btn-default" @click="delMode = false" v-show="delMode">取消</button>
          <el-checkbox v-show="delMode" v-model="checkAll" :indeterminate="isIndeterminate"
            @change="handleCheckAllChange">
            全选
          </el-checkbox>
        </div>
      </div>

      <!-- 表格 -->

    </div>

    <div class="event-table-container">
      <el-checkbox-group v-model="checkedEvents" @change="handleCheckedEventChange">
      <table class="event-table">
        <thead>
          <tr>
            <th v-show="delMode"></th>
            <th>序号</th>
            <th>标题</th>
            <th>事件信息</th>
            <th>开始时间</th>
            <th>结束时间</th>
            <th>操作</th>
          </tr>
        </thead>
        <tbody v-show="events.length > 0">
          <tr v-for="(event, index) in events" :key="event.id">
            <td style="min-width: 30px;" v-show="delMode">
              <el-checkbox :key="event.id" :value="event.id">
              </el-checkbox>
            </td>
            <td style="min-width: 50px;">{{ index + 1 }}</td>
            <td style="min-width: 110px;text-align: center;">{{ event.title }}</td>
            <td style="min-width: 110px;white-space: normal;">
              {{ event.description }}
            </td>
            <td style="min-width: 110px;">{{ dayjs(event.start_time).format('YYYY-MM-DD') }}</td>
            <td style="min-width: 110px;">{{ dayjs(event.end_time).format('YYYY-MM-DD') }}</td>
            <td style="min-width: 150px;">
              <button class="btn-edit" @click="showEdit(event)">编辑</button>
              <button class="btn-delete" @click="deleteOneEvent(event)">删除</button>
            </td>
          </tr>
        </tbody>
        <tbody v-show="events.length === 0">
          <tr>
            <td colspan="5" style="text-align: center;font-size: 20px;background-color: #fff;height: 100px;">暂无事件</td>
          </tr>
        </tbody>
      </table>
      </el-checkbox-group>
    </div>
  </div>

  <div class="form-card" v-show="docCard">
    <div @click="hiddenDocCard" class="cancel">&times;</div>
    <h2 class="form-title">批量新建事件</h2>
    <el-upload class="upload-demo" action="/" drag :before-upload="handleDoc" multiple>
      <el-icon class="el-icon--upload"><upload-filled /></el-icon>
      <div class="el-upload__text">
        Drop file here or <em>click to upload</em>
      </div>
      <template #tip>
        <div class="el-upload__tip">
          jpg/png files with a size less than 500kb
        </div>
      </template>
    </el-upload>
    <div style="text-align: center;" class="submit-button">提交</div>
  </div>

  <div class="form-card" v-show="showCard">
    <div @click="hiddenCard" class="cancel">&times;</div>
    <h2 class="form-title">事件信息</h2>
    <form>
      <div class="form-group">
        <label for="event_title" class="form-label">事件标题</label>
        <input v-model="event.title" type="text" id="event_title" class="form-input" placeholder="请输入事件标题" required>
      </div>
      <div class="form-group">
        <label for="event_time" class="form-label">事件时间</label>
        <!-- <input v-model="event.start_time" type="date" id="event_time" class="form-input" required> -->
        <el-date-picker v-model="event.start_time" type="datetime" placeholder="选择事件开始时间"
          style="display: inline-block;width: 50%;" size="large" />
        <el-date-picker v-model="event.end_time" type="datetime" placeholder="选择事件结束时间"
          style="display: inline-block;width: 50%;" size="large" />
      </div>
      <div class="form-group">
        <label for="message" class="form-label">事件详情</label>
        <textarea v-model="event.description" id="message" class="form-input" placeholder="请输入事件描述"></textarea>
      </div>
      <div class="form-group">
        <label for="message" class="form-label">事件提示</label>
        <textarea v-model="event.prompt" id="message" class="form-input" placeholder="请输入事件提示"></textarea>
      </div>
      <div v-show="!is_add" @click="handleEdit" style="text-align: center;" class="submit-button">提交</div>
      <div v-show="is_add" @click="handleCreate" style="text-align: center;" class="submit-button">提交</div>
    </form>
  </div>

  <div v-show="cover" class="covering"></div>
</template>

<style scoped>
.covering {
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, .4);
  position: fixed;
  top: 0;
  left: 0;
  z-index: 1000;
}

.form-card {
  background-color: white;
  border-radius: 10px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  width: 100%;
  max-width: 480px;
  padding: 30px;
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  z-index: 1001;
  box-sizing: border-box;
}

.form-title {
  font-size: 22px;
  color: #333;
  margin-bottom: 15px;
  text-align: center;
  font-weight: 600;
  margin-top: 3px;
}

.form-group {
  margin-bottom: 10px;
}

.form-label {
  display: block;
  margin-bottom: 8px;
  font-weight: 500;
  color: #555;
}

.form-input {
  width: calc(100% - 30px);
  padding: 12px 15px;
  border: 1px solid #ddd;
  border-radius: 6px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.form-input:focus {
  border-color: #4a90e2;
  outline: none;
  box-shadow: 0 0 0 2px rgba(74, 144, 226, 0.2);
}

textarea.form-input {
  min-height: 50px;
  resize: vertical;
  resize: none;
}

.submit-button {
  width: calc(100% - 20px);
  padding: 12px;
  background-color: #4a90e2;
  color: white;
  border: none;
  border-radius: 6px;
  font-size: 16px;
  font-weight: 500;
  cursor: pointer;
  transition: background-color 0.3s;
  text-align: center;
}

.submit-btn:hover {
  background-color: #3a7bc8;
}

input[type="datetime-local"] {
  height: 40px;
}

input[type="datetime-local"]::-webkit-calendar-picker-indicator {
  cursor: pointer;
  padding: 5px;
  border-radius: 3px;
}

input[type="datetime-local"]::-webkit-calendar-picker-indicator:hover {
  background-color: #f0f0f0;
}

/* 主内容区 */

/* 事件管理容器 */
.event-management {
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

/* 操作栏 */
.action-bar {
  display: flex;
  justify-content: space-between;
  flex-wrap: wrap;
  gap: 15px;
}

.search-box {
  display: flex;
  gap: 10px;
  flex-grow: 1;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px;
  min-width: 200px;
  font-size: 14px;
}

.search-box select {
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  background: white;
  font-size: 14px;
}

.action-buttons {
  display: flex;
  gap: 10px;
}

.cancel {
  font-size: 26px;
  position: absolute;
  top: 28px;
  right: 30px;
}

/* 按钮样式 */
button {
  padding: 6px 10px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  display: flex;
  align-items: center;
  gap: 5px;
  border: 1px solid transparent;
  transition: all 0.3s;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
  border-color: #1890ff;
  height: 38px;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-default {
  background: white;
  border-color: #d9d9d9;
  color: #333;
  height: 38px;
}

.btn-default:hover {
  border-color: #1890ff;
  color: #1890ff;
}

.btn-edit {
  background: #f0f9ff;
  border-color: #91d5ff;
  color: #1890ff;
  /* width: 40px; */
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  margin-right: 5px;
}

.btn-delete {
  background: #fff2f0;
  border-color: #ffccc7;
  color: #ff4d4f;
  /* width: 40px; */
  display: inline-block;
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  margin-right: 5px;
}

.icon {
  font-size: 16px;
}

/* 表格容器 */
.event-table-container {
  overflow-x: auto;
  margin-bottom: 20px;
  margin-top: 10px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
  padding: 20px;
}

/* 表格样式 */
.event-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 14px;
  min-width: 700px;
}

.event-table th,
.event-table td {
  padding: 12px 15px;
  text-align: center;
  border-bottom: 1px solid #f0f0f0;
  overflow-wrap: break-word;
  overflow: hidden;
  white-space: normal; /* 允许换行 */
  word-break: break-all;
  box-sizing: border-box;
}

.event-table th {
  background-color: #fafafa;
  color: #666;
  font-weight: 500;
  white-space: nowrap;
  text-align: center;
}

.event-table tr:hover {
  background-color: #fafafa;
}

/* 标签样式 */
.event-tag {
  display: inline-block;
  padding: 2px 8px;
  border-radius: 4px;
  font-size: 12px;
}

.tag-bug {
  background-color: #fff2f0;
  color: #ff4d4f;
  border: 1px solid #ffccc7;
}

.tag-feature {
  background-color: #f6ffed;
  color: #52c41a;
  border: 1px solid #b7eb8f;
}

.tag-task {
  background-color: #fffbe6;
  color: #faad14;
  border: 1px solid #ffe58f;
}

/* 优先级星星 */
.priority-stars {
  color: #d9d9d9;
  font-size: 16px;
  letter-spacing: 2px;
}

.priority-stars .active {
  color: #faad14;
}

/* 开关样式 */
.switch {
  position: relative;
  display: inline-block;
  width: 50px;
  height: 24px;
}

.switch input {
  opacity: 0;
  width: 0;
  height: 0;
}

.slider {
  position: absolute;
  cursor: pointer;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background-color: #ccc;
  transition: .4s;
  border-radius: 24px;
}

.slider:before {
  position: absolute;
  content: "";
  height: 16px;
  width: 16px;
  left: 4px;
  bottom: 4px;
  background-color: white;
  transition: .4s;
  border-radius: 50%;
}

input:checked+.slider {
  background-color: #52c41a;
}

input:checked+.slider:before {
  transform: translateX(26px);
}

/* 分页 */
.pagination {
  display: flex;
  justify-content: center;
  gap: 8px;
  margin-top: 20px;
}

.pagination button {
  min-width: 32px;
  height: 32px;
  padding: 0 8px;
  border: 1px solid #d9d9d9;
  background: white;
  color: #333;
}

.pagination button.active {
  border-color: #1890ff;
  color: #1890ff;
  font-weight: 500;
}

.pagination button:disabled {
  color: #d9d9d9;
  cursor: not-allowed;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .main-content {
    margin-left: 0;
  }

  .action-bar {
    flex-direction: column;
  }

  .search-box {
    flex-direction: column;
  }

  .action-buttons {
    justify-content: flex-start;
  }
}

@media (max-width: 480px) {
  .action-bar .search-box input {
    width: 100%;
    box-sizing: border-box;
  }
}
</style>
