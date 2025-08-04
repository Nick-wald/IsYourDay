<script setup>
import { ref, onMounted } from 'vue';
import { addEventOrMsg, getUserEvent, delEventOrMsg, updateEventOrMsg } from '../api/event.ts'
import { editUserMsg, getAllUser } from '../api/user.ts'
import dayjs from 'dayjs'
import { useRoute } from 'vue-router'


const route = useRoute()
const avatarInput = ref(null);
const isEditing = ref(false);
const isEditingAvatar = ref(false);
const is_add = ref(true)
const user_pk = ref('')
const sex = ['不明', '男', '女']
const formData = ref({
  real_name: '',
  birthday: '',
  sex: 0,
  tel: '',
  location: '',
  prompt: '',
  identify: '',
  QQ:'',
  wechat: '',
  email:''
});
const cover = ref(false)
// 用户数据
const user = ref({});
const imgUrl = ref('')
const options = ref([])
// 编辑时的用户数据副本
const editUser = ref({});


const getList = async () => {
  const res = await getAllUser()
  options.value = res.data.results.map(item => {
    return {
      label: item.username,
      value: item.id
    }
  })
}

// 上传头像
const changeAvatar = (e) => {
  const file = e.target.files[0]
  if (file) {
    editUser.value.avatar = file
    user.value.avatar = URL.createObjectURL(file)
    imgUrl.value = URL.createObjectURL(file)
  }
}

// 新建用户详情信息
const addDetail = async () => {
  formData.value.pk = user_pk.value
  formData.value.type = 'info'
  if (!formData.value.birthday) {
    delete formData.value.birthday
  }
  const res = await addEventOrMsg(formData.value)
  if (res.status === 200) {
    ElMessage.success('新建成功')
  }
  findDetail()
  is_add.value = false
}

// 查找用户详情信息
const findDetail = async () => {
  const res = await getUserEvent({ pk: user_pk.value, types: 'info' })
  if (res.status === 200) {
    ElMessage.success('查找成功')
  }

  user.value = { ...res.data }
  user.value.avatar = 'https://api.nickwald.top/' + user.value.avatar + `?t=${new Date().getTime()}`
  editUser.value = { ...res.data }
  // editUser.value.avatar = 'https://api.nickwald.top/'+ editUser.value.avatar
  is_add.value = false
}

// 删除用户详情信息
const delDetail = async () => {
  const data = { pk: editUser.value.account_info_id, type: 'info' }
  const res = await delEventOrMsg(data)
  if (res.status === 200) {
    ElMessage.success('删除成功')
  }
  findDetail()
  is_add.value = true
  isEditing.value = false
}

// 进入新建模式
const startAdd = () => {
  is_add.value = true
}

// 进入编辑模式
const startEditing = () => {
  isEditing.value = true;
};

// 取消编辑
const cancelEditing = () => {
  isEditing.value = false;
  isEditingAvatar.value = false;
};

// 保存更改
const saveChanges = async () => {
  const data = {
    qq: editUser.value.QQ,
    type: 'info',
    pk: editUser.value.account_info_id,
    birthday: editUser.value.birth,
    location: editUser.value.location,
    email: editUser.value.email,
    phone: editUser.value.phone,
    sex: editUser.value.sex,
    username: editUser.value.username,
    real_name: editUser.value.real_name,
    prompt: editUser.value.prompt,
    // avatar: editUser.value.avatar
  }
  const info = new FormData()

  // info.append('avatar', editUser.value.avatar)
  info.append('pk', user_pk.value)
  info.append('email', editUser.value.email)
  // info.append('qq', editUser.value.QQ)
  info.append('username', editUser.value.username)

  // const info = {
  //   pk: user_pk.value,
  //   email: editUser.value.email,
  //   username: editUser.value.username,
  //   qq: editUser.value.QQ,
  // }
  await editUserMsg(info)
  await updateEventOrMsg(data)
  isEditing.value = false;
  isEditingAvatar.value = false;
  // 这里可以添加API调用保存数据
  findDetail()
  // user.value.avatar = imgUrl.value
};



onMounted(() => {
  // getList()
  // if (route.query.pk) {
  //   user_pk.value = route.query.pk
  //   findDetail()
  // }
  
})
</script>

<template>
  <!-- <div class="header">
    <h2>用户详情</h2>
  </div>
  <div class="card">
    <div class="search-box" style="margin: 0;">
      <el-select filterable v-model="user_pk" size="large" placeholder="请选择需要查询的用户" style="width: 100%;">
        <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
      </el-select>
      <button style="margin-left: 5px;border-radius: 5px;" @click="findDetail">搜索</button>
      <button style="margin-left: 5px;border-radius: 5px;" @click="startAdd">添加</button>
    </div>
  </div> -->
  <div v-show="!is_add" class="user-profile-container">
    <div class="user-profile-card">
      <div class="user-header">
        <div class="avater">
          <label>
            <img :src="user.avatar" alt="">
            <input v-if="isEditing" style="display: none;" type="file" @change="changeAvatar">
          </label>
        </div>
        <h2>用户 {{ user.username }} 的信息</h2>
      </div>

      <div class="user-details">

        <div class="detail-item">
          <span class="detail-label">用户名:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.username }}</span>
          <input v-else v-model="editUser.username" type="text" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">姓名:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.real_name || '未设置' }}</span>
          <input v-else v-model="editUser.real_name" type="text" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">性别:</span>
          <span v-if="!isEditing" class="detail-value">{{ sex[user.sex] }}</span>
          <select class="edit-input" v-else v-model="editUser.sex">
            <option value="0">不明</option>
            <option value="1">男</option>
            <option value="2">女</option>
          </select>
        </div>

        <div class="detail-item">
          <span class="detail-label">位置:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.location || '未设置' }}</span>
          <input v-else v-model="editUser.location" type="text" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">邮箱:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.email }}</span>
          <input v-else v-model="editUser.email" type="email" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">电话:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.phone || '未设置' }}</span>
          <input v-else v-model="editUser.phone" type="tel" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">QQ:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.QQ }}</span>
          <input v-else v-model="editUser.QQ" type="tel" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">加入时间:</span>
          <span class="detail-value">{{ dayjs(user.date_joined).format('YYYY-MM-DD') }}</span>
        </div>

        <div class="detail-item">
          <span class="detail-label">身份:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.identify || '未设置' }}</span>
          <input v-else v-model="editUser.identify" type="text" class="edit-input" />
        </div>

        <div class="detail-item">
          <span class="detail-label">生日:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.birthday || '未设置' }}</span>
          <input v-else v-model="editUser.birthday" type="date" class="edit-input" />
        </div>

        <div class="detail-item" style="grid-column: 1 / -1;">
          <span class="detail-label">提示:</span>
          <span v-if="!isEditing" class="detail-value">{{ user.prompt || '暂无提示' }}</span>
          <textarea v-else v-model="editUser.prompt" class="edit-textarea"></textarea>
        </div>
      </div>

      <div v-show="!user.is_superuser" class="action-buttons">
        <button v-if="!user.account_info_id" class="edit-btn" @click="startAdd">添加</button>
        <button v-if="!isEditing && user.account_info_id" @click="startEditing" class="edit-btn">
          编辑信息
        </button>
        <div v-else-if="user.account_info_id" class="edit-mode-buttons">
          <button @click="saveChanges" class="save-btn">保存更改</button>
          <button @click="delDetail" class="cancel-btn">删除</button>
          <button @click="cancelEditing" class="default-btn">取消</button>
        </div>
      </div>
    </div>
  </div>
  <div v-show="cover" class="covering"></div>

  <div v-show="is_add" class="form-container">
    <h2>用户信息</h2>
    <form @submit.prevent="submitForm" class="user-form">
      <!-- 真实姓名 -->
      <div class="form-group">
        <label for="real_name">姓名</label>
        <input type="text" v-model="formData.real_name" placeholder="请输入您的真实姓名" />
      </div>

      <!-- 邮箱 -->
       <div class="form-group">
        <label for="email">邮箱</label>
        <input type="text" v-model="formData.email" placeholder="请输入您的邮箱" />
      </div>

      <!-- QQ -->
       <div class="form-group">
        <label for="QQ">QQ</label>
        <input type="text" v-model="formData.QQ" placeholder="请输入您的QQ" />
      </div>

      <!-- wechat -->
      <div class="form-group">
        <label for="wechat">微信</label>
        <input type="text" v-model="formData.wechat" placeholder="请输入您的微信" />
      </div>

      <!-- 生日 -->
      <div class="form-group">
        <label for="birthday">生日</label>
        <input type="date" v-model="formData.birthday" />
      </div>

      <!-- 性别 -->
      <div class="form-group">
        <label for="sex">性别</label>
        <div class="radio-group">
          <label>
            <input type="radio" v-model="formData.sex" value="1" />
            男
          </label>
          <label>
            <input type="radio" v-model="formData.sex" value="2" />
            女
          </label>
          <label>
            <input type="radio" v-model="formData.sex" value="0" />
            不明
          </label>
        </div>
      </div>

      <!-- 电话号码 -->
      <div class="form-group">
        <label for="phone">电话号码</label>
        <input type="tel" v-model="formData.phone" placeholder="请输入您的电话号码" />
      </div>

      <!-- 所在地 -->
      <div class="form-group">
        <label for="location">所在地</label>
        <input type="text" v-model="formData.location" placeholder="请输入您的所在地" />
      </div>

      <!-- 身份 -->
      <div class="form-group">
        <label for="identify">身份</label>
        <input type="text" placeholder="请输入您的身份" v-model="formData.identify">
      </div>

      <!-- 备注/提示 -->
      <div class="form-group">
        <label for="prompt">提示</label>
        <textarea id="prompt" v-model="formData.prompt" rows="4" placeholder="请填写提示信息"></textarea>
      </div>

      <button @click="addDetail" type="submit" class="submit-btn">提交</button>
    </form>
  </div>

  <!-- <div v-show="!user.username" class="white-space">暂无用户相关信息，请前往搜索</div> -->
</template>

<style scoped>
/* 基础样式重置 */
* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

.header {
  padding: 12px;
  background-color: white;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  margin-bottom: 20px;
  border-radius: 8px;
}

.header h2 {
  margin: 0;
  color: #333;
  font-size: 1.5rem;
}

/* 卡片基础样式 */
.card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 20px;
  margin-bottom: 24px;
}

.white-space {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 50px 20px;
  text-align: center;
  font-size: 20px;
}

/* 搜索框区域 */
.search-box {
  display: flex;
  align-items: center;
  gap: 10px;
}

.search-box input {
  flex: 1;
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: border-color 0.3s;
}

.search-box input:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.search-box button {
  padding: 12px 20px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s;
  white-space: nowrap;
}

.search-box button:hover {
  background-color: #40a9ff;
  transform: translateY(-1px);
}

/* 用户信息卡片 */
.user-profile-container {
  margin-top: 24px;
}

.user-profile-card {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.08);
  padding: 28px;
}

/* 用户头部区域 */
.user-header {
  display: flex;
  align-items: center;
  gap: 20px;
  margin-bottom: 28px;
  padding-bottom: 20px;
  border-bottom: 1px solid #f0f0f0;
}

.avater {
  width: 80px;
  height: 80px;
  border-radius: 50%;
  overflow: hidden;
  background-color: #f5f5f5;
  display: flex;
  align-items: center;
  justify-content: center;
}

.avater img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.user-header h2 {
  margin: 0;
  color: #333;
  font-size: 1.8rem;
  font-weight: 600;
}

/* 用户详情网格布局 */
.user-details {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
  margin-bottom: 28px;
}

.detail-item {
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.detail-label {
  font-weight: 500;
  color: #666;
  font-size: 15px;
}

.detail-value {
  color: #333;
  font-size: 16px;
  word-break: break-word;
}

.edit-input,
.edit-textarea {
  padding: 10px 14px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  width: 100%;
  transition: all 0.3s;
}

.edit-input:focus,
.edit-textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.edit-textarea {
  min-height: 100px;
  resize: vertical;
}

/* 操作按钮样式 */
.action-buttons {
  display: flex;
  justify-content: flex-end;
  margin-top: 28px;
  gap: 12px;
}

.edit-btn,
.save-btn,
.cancel-btn,
.default-btn {
  padding: 10px 20px;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 15px;
  transition: all 0.3s;
  min-width: 100px;
}

.edit-btn {
  background-color: #1890ff;
  color: white;
}

.edit-btn:hover {
  background-color: #40a9ff;
  transform: translateY(-1px);
}

.save-btn {
  background-color: #52c41a;
  color: white;
}

.save-btn:hover {
  background-color: #73d13d;
  transform: translateY(-1px);
}

.cancel-btn {
  background-color: #ff4d4f;
  color: white;
}

.cancel-btn:hover {
  background-color: #ff7875;
  transform: translateY(-1px);
}

.default-btn {
  background-color: #f5f5f5;
  color: #333;
}

.default-btn:hover {
  background-color: #e8e8e8;
  transform: translateY(-1px);
}

/* 遮罩层 */
.covering {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 100;
  backdrop-filter: blur(3px);
}

/* 添加表单样式 */
.form-container {
  background: #fff;
  border-radius: 12px;
  box-shadow: 0 8px 24px rgba(0, 0, 0, 0.15);
  padding: 32px;
  z-index: 101;
  width: 100%;
  box-sizing: border-box;
}

.form-container h2 {
  margin-top: 0;
  margin-bottom: 24px;
  color: #333;
  text-align: center;
  font-size: 1.8rem;
}

.user-form {
  display: grid;
  gap: 20px;
}

.form-group {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.form-group label {
  font-weight: 500;
  color: #555;
  font-size: 15px;
}

.form-group input,
.form-group textarea {
  padding: 12px 16px;
  border: 1px solid #e0e0e0;
  border-radius: 8px;
  font-size: 15px;
  transition: all 0.3s;
}

.form-group input:focus,
.form-group textarea:focus {
  outline: none;
  border-color: #1890ff;
  box-shadow: 0 0 0 2px rgba(24, 144, 255, 0.2);
}

.form-group textarea {
  min-height: 120px;
  resize: vertical;
}

.radio-group {
  display: flex;
  gap: 20px;
  margin-top: 6px;
}

.radio-group label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  font-size: 15px;
}

.submit-btn {
  padding: 12px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 8px;
  cursor: pointer;
  font-size: 16px;
  margin-top: 12px;
  transition: all 0.3s;
}

.submit-btn:hover {
  background-color: #40a9ff;
  transform: translateY(-1px);
}

/* 平板适配 (768px-1024px) */
@media (max-width: 1024px) {
  /* .user-details {
    grid-template-columns: 1fr;
    gap: 20px;
  } */

  .user-profile-card,
  .card {
    padding: 24px;
  }

  .user-header {
    /* flex-direction: column; */
    text-align: center;
    gap: 16px;
  }

  .user-header h2 {
    font-size: 1.6rem;
  }

  .form-container {
    padding: 28px;
  }
}

/* 手机适配 (480px-768px) */
@media (max-width: 768px) {

  .user-profile-card {
    padding: 20px;
  }

  .avater {
    width: 70px;
    height: 70px;
  }

  .user-header h2 {
    font-size: 1.4rem;
  }

  .action-buttons {
    flex-direction: column;
  }

  .form-container {
    width: 95%;
    padding: 24px;
  }

  .radio-group {
    flex-direction: column;
    gap: 12px;
  }
}

/* 小手机适配 (<480px) */
@media (max-width: 480px) {
  .search-box {
    /* flex-direction: column; */
    /* gap: 12px; */
    /* flex-wrap: wrap; */
    display: block;
  }

  .search-box::after {
    content: '';
    display: block;
    clear: both;
  }

  .search-box button {
    width: calc(50% - 5px);
    float: left;
  }

  .search-box input {
    width: 100%;
    margin-bottom: 10px;
  }

  .card {
    padding: 16px;
  }

  .user-profile-card {
    padding: 16px;
  }

  .avater {
    width: 60px;
    height: 60px;
  }

  .user-header h2 {
    font-size: 1.3rem;
  }

  .user-header {
    flex-direction: column;
    text-align: center;
    gap: 16px;
  }

  .detail-label {
    font-size: 14px;
  }

  .detail-value {
    font-size: 15px;
  }

  .edit-input,
  .edit-textarea {
    padding: 8px 12px;
    font-size: 14px;
  }

  .form-container {
    padding: 20px;
  }

  .form-container h2 {
    font-size: 1.4rem;
  }

  .form-group label {
    font-size: 14px;
  }

  .form-group input,
  .form-group textarea {
    padding: 10px 14px;
    font-size: 14px;
  }

  .submit-btn {
    font-size: 15px;
  }
}
</style>