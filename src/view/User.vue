<script setup lang="ts">
// import { authInit } from '../utils/authUtils'
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
// import './assets/style.css'
import { getUserList, searchUser, delVirtualUser } from '../api/user'
import { ElMessage } from 'element-plus'
import { UploadFilled } from '@element-plus/icons-vue'
import UserMsgForm from '@/components/UserMsgForm.vue'
// import { IsYourDayService } from '@/client'

const router = useRouter()

const direction = ref('rtl')
const size = ref('60%')
// authInit(true)

const userList = ref<any>([])
const count = ref(0)
const page_num = ref(0)
const total = ref(0)
const page_size = ref(5)
const showCard = ref(false)
const inp_value = ref('')
const userMsg = ref<any>({})
const is_edit = ref(false)
const password = ref('')
const id = ref('')
const showDel = ref(false)
// const cover = ref(false)
const docCard = ref(false)
const doc = ref()
const role = ref('id')
const type = ref(true)
const userId = ref('')

const delMode = ref(false)
const checkAll = ref(false)
const checkedUser = ref<string[]>([])
const isIndeterminate = ref(true)

const goDetail = async (item: any) => {
  if (delMode.value) {
    return
  }
  const width = window.innerWidth

  if (width < 768) {
    direction.value = 'btt'
    size.value = '65%'
  }
  else {
    direction.value = 'rtl'
    size.value = '60%'
  }


  userId.value = item.id
  type.value = false
  showCard.value = true
}

const goTask = (item: any) => {
  router.push({
    path: '/event',
    query: { pk: item.id }
  })
}

const showDocCard = () => {
  docCard.value = true
}

const hiddenDocCard = () => {
  docCard.value = false
}

// // // // const hiddenCard = () => {
// // //   showCard.value = false
// //   cover.value = false
// }
const hiddenDel = () => {
  showDel.value = false
  // cover.value = false
}

const getList = async (page = 0, page_size = 5) => {
  const skip = page*page_size
  const res = await getUserList(skip, page_size)

  // count.value = res.data.pagination
  total.value = res.data.pagination.total_pages
  userList.value = res.data.items
}

const idFind = async () => {
  if(inp_value.value) {
    const res = await searchUser(inp_value.value)
    if (res.status === 200) {
      ElMessage.success('查找用户成功')
      userList.value = res.data.items
      total.value = 0
    }
  }
  else {
    getList()
  }
  //   userList.value.push(res.data)
}

const addCard = () => {
  const width = window.innerWidth

  if (width < 768) {
    direction.value = 'btt'
    size.value = '65%'
  }
  else {
    direction.value = 'rtl'
    size.value = '60%'
  }
  userId.value = ''
  type.value = true
  showCard.value = true
  // is_edit.value = false
}

const handleCheckAllChange = (val: any) => {
  const users = userList.value.map((item: any) => {
    return item.id
  })
  checkedUser.value = val ? users : []
  isIndeterminate.value = false
}

const handleCheckedUserChange = (value: any) => {
  const users = userList.value.map((item: any) => {
    return item.id
  })
  const checkedCount = value.length
  checkAll.value = checkedCount === users.length
  isIndeterminate.value = checkedCount > 0 && checkedCount < users.length
}

const deleteUser = async () => {
  await delVirtualUser(checkedUser.value)
  getList()
}

const delCard = (id: string) => {
  checkedUser.value = []
  checkedUser.value.push(id)
  deleteUser()
  checkedUser.value = []
}

const handleDoc = (file: any) => {
  doc.value = file
  return false
}

const submitUpload = async () => {
  const access = localStorage.getItem('access')

  const response = await fetch('http://127.0.0.1/v1/workflows/run', {
    method: 'POST',
    headers: {
      'Authorization': 'Bearer app-fQteVsq8J6N9ttFfk7mPmLR5',
      'Content-Type': 'application/json'
    },
    body: JSON.stringify({
      inputs: {
        "file": [
          {
            "type": "xlsx",
            "transfer_method": "local_file",
            "upload_file_id": "c5f907cb-bb1e-465b-b4b7-28a8b41edace"
          }
        ],
        "token": 'Bearer ' + access,
        "type": "info"
      },
      response_mode: "streaming",
      user: "xjs123"
    })
  });

}


onMounted(() => {
  getList()
  // userMsg.value = user

})

</script>

<template>
  <div class="header">
    <h2>用户管理</h2>
  </div>
  <!-- <div v-show="cover" class="covering"></div> -->
  <!-- 搜索和添加用户 -->
  <div class="card">
    <div class="search-box">
      <!-- <select v-model="role" style="border-color: #ccc;border-radius: 5px;margin-right: 5px;width: 80px;">
        <option value="id">ID查询</option>
        <option value="email">邮箱查询</option>
        <option value="username">用户名查询</option>
      </select> -->
      <input v-model="inp_value" type="text" placeholder="搜索用户姓名...">
      <button @click="idFind">搜索</button>
    </div>
    <button @click="addCard" class="btn btn-primary">添加用户</button>
    <!-- <button @click="showDocCard" class="btn btn-primary">批量上传</button> -->
    <button v-show="!delMode" @click="delMode = true" class="btn btn-primary">批量删除</button>
    <button class="btn btn-danger" @click="deleteUser" v-show="delMode">删除</button>
    <button class="btn btn-default" @click="delMode = false" v-show="delMode">取消</button>
    <el-checkbox v-show="delMode" v-model="checkAll" :indeterminate="isIndeterminate" @change="handleCheckAllChange">
      全选
    </el-checkbox>
  </div>

  <!-- 用户列表表格 -->
  <div class="card">
    <div class="card-header">
      <h3>用户列表</h3>
      <div>
        <select @change="getList(page_num, page_size)" v-model="page_size" class="select"
          style="width: auto; display: inline-block;">
          <option value="5">每页5条</option>
          <option value="10">每页10条</option>
          <option value="20">每页20条</option>
        </select>
      </div>
    </div>
    <el-checkbox-group v-model="checkedUser" @change="handleCheckedUserChange">
      <table>
        <thead>
          <tr>
            <th v-if="delMode">

            </th>
            <th>序号</th>
            <th>姓名</th>
            <!-- <th>电话</th> -->
            <th>邮箱</th>
            <th>操作</th>
          </tr>
        </thead>
        <!-- <el-checkbox-group v-model="checkedUser" @change="handleCheckedUserChange"> -->
        <tbody>
          <tr class="white-box" v-show="userList.length === 0">
            <td colspan="4">
              未获取到用户列表
            </td>
          </tr>
          <tr v-for="(item, index) in userList" @click="goDetail(item)">
            <td v-show="delMode">
              <el-checkbox :key="item.id" :value="item.id">

              </el-checkbox>
            </td>
            <td>{{ page_size * (page_num) + index + 1 }}</td>
            <td>{{ (item as any).real_name }}</td>
            <!-- <td>{{ (item as any).tel }}</td> -->
            <td>{{ (item as any).email }}</td>
            <td>
              <button class="btn btn-primary" @click.stop="goTask(item)">事件</button>
              <!-- <button class="btn email-btn" @click.stop="goEmail(item)">邮件</button> -->
              <button v-on:click.stop="delCard((item as any).id)" class="btn btn-danger">删除</button>
            </td>
          </tr>
        </tbody>
        <!-- </el-checkbox-group> -->
      </table>
    </el-checkbox-group>
    <!-- 分页 -->
    <div class="pagination-container">
      <div class="pagination">
        <button @click="getList(--page_num, page_size)" class="page-btn prev-btn" :disabled="page_num == 0">上一页</button>
        <div class="page-numbers">
          {{ page_num + 1 }}
        </div>
        <button @click="getList(++page_num, page_size)" class="page-btn next-btn"
          :disabled="page_num + 1 >= total">下一页</button>
      </div>
    </div>
  </div>

  <!-- 批量导入 -->
  <div v-show="docCard" class="add-card">
    <div class="card-header">
      <h3>批量上传</h3>
      <button @click="hiddenDocCard" class="cancle">&times;</button>
    </div>
    <el-upload :show-file-list="true" class="upload-demo" action="/" drag :before-upload="handleDoc" multiple>
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
    <div type="submit" @click="submitUpload" class="btn btn-success">提交</div>
  </div>

  <!-- 添加/编辑用户模态框 (默认隐藏) -->
  <!-- <div class="add-card" v-show="showCard" id="userForm">
    <div class="card-header">
      <h3>添加用户</h3>
      <button @click="hiddenCard" class="cancle">&times;</button>
    </div>
    <form>
      <div class="form-group">
        <label for="username">用户名</label>
        <input v-model="userMsg.username" type="text" class="form-control" required>
      </div>
      <div class="form-group">
        <label for="qq">QQ</label>
        <input v-model="userMsg.QQ" type="text" class="form-control" required>
      </div>
      <div class="form-group">
        <label for="email">邮箱</label>
        <input v-model="userMsg.email" type="email" class="form-control" required>
      </div>
      <div class="form-group" v-show="!is_edit">
        <label for="password">密码</label>
        <input v-model="userMsg.password" type="password" class="form-control" required>
      </div>
      <div @click="userAdd" v-show="!is_edit" type="submit" class="btn btn-success">添加</div>
    </form>
  </div> -->

  <div class="getPwd" v-show="showDel">
    <h2>请输入密码</h2>
    <input class="pwd-inp" type="password" v-model="password">
    <button class="Del-btn" @click="deleteUser()">删除</button>
    <button class="cancelDel" @click="hiddenDel">取消</button>
  </div>

  <el-drawer @close="getList" :destroy-on-close="true" v-model="showCard" :with-header="false" :direction="direction" class="demo-drawer"
    :size="size">
    <UserMsgForm :is_add="type" @changeMsg="getList" :userId="userId" />
  </el-drawer>
</template>

<style scoped>
/* 基础样式 */

.white-box{
  height: 100px;
  background-color: #fff;
}
.white-box td{
  text-align: center;
  background-color: #fff;
  font-size: 20px;
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

.covering {
  position: fixed;
  top: 0;
  left: 0;
  width: 100vw;
  height: 100vh;
  background-color: rgba(0, 0, 0, 0.5);
  z-index: 1000;
}

/* 批量上传 */
/* .show{
  width: calc(100% - 10px);
  height: 160px;
  text-align: center;
  border: 1px dashed #ccc;
  border-radius: 10px;
}
.show .el-icon--upload{
  font-size: 100px;
  color: #ccc;
  margin-bottom: 20px;
}
.show .el-upload__text{
  color: #aaa;
} */


/* 卡片样式 */
.card {
  background: #fff;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 20px;
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.card-header h3 {
  margin: 0;
  font-size: 1.2rem;
  color: #333;
}

/* 搜索框样式 */

.select {
  width: 200px;
  height: 36px;
}

.search-box {
  display: flex;
  margin-bottom: 15px;
}

.search-box input {
  flex: 1;
  padding: 10px 15px;
  border: 1px solid #ddd;
  border-radius: 4px 0 0 4px;
  font-size: 14px;
}

.search-box button {
  padding: 10px 15px;
  background-color: #1890ff;
  color: white;
  border: none;
  border-radius: 0 4px 4px 0;
  cursor: pointer;
  transition: background-color 0.3s;
}

.search-box button:hover {
  background-color: #40a9ff;
}

/* 表格样式 */
table {
  width: 100%;
  border-collapse: collapse;
  margin-bottom: 20px;
}

th,
td {
  padding: 12px 15px;
  text-align: left;
  border-bottom: 1px solid #e0e0e0;
  font-size: 16px;
  height: 10px;
}

th {
  background-color: #f5f5f5;
  font-weight: 500;
  color: #333;
}

tr:hover {
  background-color: #f9f9f9;
}

/* 按钮样式 */
.btn {
  padding: 8px 12px;
  border-radius: 4px;
  font-size: 14px;
  cursor: pointer;
  transition: all 0.3s;
  border: none;
  margin-right: 5px;
}

.btn-primary {
  background-color: #1890ff;
  color: white;
}

.btn-primary:hover {
  background-color: #40a9ff;
}

.btn-default {
  background-color: #fff;
  border: 0.5px solid #000;
  color: 000;
}

.btn-danger {
  background-color: #ff4d4f;
  color: white;
}

.btn-danger:hover {
  background-color: #ff7875;
}

.btn-success {
  background-color: #52c41a;
  color: white;
  padding: 10px 20px;
  margin-top: 15px;
  text-align: center;
  font-size: 18px;
}

.btn-success:hover {
  background-color: #73d13d;
}

.email-btn {
  background-color: #722ed1;
  color: white;
}

.email-btn:hover {
  background-color: #9254de;
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

/* 表单组样式 */
.add-card {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  width: 60%;
  max-width: 500px;
  background: white;
  border-radius: 10px;
  box-shadow: 0 5px 15px rgba(0, 0, 0, 0.3);
  z-index: 1000;
  padding: 20px;
}

.cancle {
  position: absolute;
  right: 20px;
  top: 20px;
  border: 0;
  background: #fff;
  font-size: 20px;
}

.form-group {
  margin-bottom: 15px;
}

.form-group label {
  display: block;
  margin-bottom: 5px;
  font-weight: bold;
}

.form-group .form-control {
  width: calc(100% - 20px);
  padding: 10px;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 1rem;
}

/*............. */

/* 删除确认框 */
.getPwd {
  position: fixed;
  top: 50%;
  left: 50%;
  transform: translate(-50%, -50%);
  background: #fff;
  padding: 20px;
  border-radius: 8px;
  z-index: 1000;
  width: 90%;
  max-width: 400px;
  text-align: center;
}

.getPwd h2 {
  margin-top: 0;
  margin-bottom: 20px;
  font-size: 1.2rem;
}

.pwd-inp {
  width: calc(100% - 30px);
  padding: 10px 15px;
  border: 1px solid #d9d9d9;
  border-radius: 4px;
  margin-bottom: 15px;
}

.Del-btn,
.cancelDel {
  padding: 8px 20px;
  margin: 0 10px;
  border-radius: 4px;
  cursor: pointer;
}

.Del-btn {
  background-color: #ff4d4f;
  color: white;
  border: none;
}

.Del-btn:hover {
  background-color: #ff7875;
}

.cancelDel {
  background-color: #f5f5f5;
  border: 1px solid #d9d9d9;
}

.cancelDel:hover {
  background-color: #e8e8e8;
}

/* 平板适配 (768px-1024px) */
@media (max-width: 1024px) {
  .card {
    padding: 15px;
  }

  th,
  td {
    padding: 10px 12px;
    font-size: 14px;
  }

  /* .btn {
    padding: 6px 10px;
    font-size: 13px;
  } */

  .btn-success {
    font-size: 20px;
  }
}

/* 手机适配 (<768px) */
@media (max-width: 768px) {
  .card {
    padding: 12px;
    margin-bottom: 15px;
  }


  table {
    display: block;
    width: 100%;
    max-width: 520px;
    overflow-x: auto;
    white-space: nowrap;
  }

  th {
    width: 100%;
  }

  th,
  td {
    padding: 8px 10px;
    font-size: 13px;
  }

  /* .btn {
    padding: 5px 8px;
    font-size: 12px;
    margin-bottom: 5px;
  } */

  .card-header {
    align-items: flex-start;
  }

  .card-header h3 {
    margin-bottom: 10px;
  }

  .select {
    height: 30px;
    width: 180px;
  }

  .add-card {
    width: 100%;
    padding: 16px;
    box-sizing: border-box;
  }

  .form-control {
    padding: 8px 12px;
  }

  .getPwd {
    width: 95%;
    padding: 15px;
  }
}

/* 小手机适配 (<480px) */
@media (max-width: 480px) {
  .search-box input {
    width: 100px;
  }

  .card-header h3 {
    font-size: 1.1rem;
  }

  th,
  td {
    padding: 6px 8px;
    font-size: 12px;
  }

  /* .btn {
    padding: 4px 6px;
    font-size: 11px;
  } */

  .page-btn {
    padding: 6px 10px;
    font-size: 12px;
  }

  .page-numbers {
    padding: 6px 10px;
    font-size: 12px;
  }
}
</style>