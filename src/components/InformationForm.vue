<template>
  <div class="page-container min-h-screen bg-gray-50 py-10 px-4 sm:px-6 lg:px-8">
    <div class="max-w-6xl mx-auto">
      <!-- 核心标题 -->
      <div class="text-center mb-6">
        <h1 class="main-title">工作流管理及记录</h1>
      </div>

      <!-- 核心表格 -->
      <div class="bg-white rounded-lg border border-gray-200">
        <!-- 操作按钮区 -->
        <div class="flex items-center p-4 bg-gray-50 border-b">
          <!-- 发送相关功能已移除 -->
        </div>
        
        <el-table 
          :data="workflowResults" 
          border 
          stripe 
          style="width: 100%"
        >
          <!-- 表格列定义 -->
          <el-table-column 
            label="序号" 
            width="80"
            align="center"
          >
            <template #default="scope">
              <span class="font-medium text-gray-700">
                {{ scope.$index + 1 }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="user_id" 
            label="用户ID" 
            width="120"
            align="center"
          />
          
          <el-table-column 
            prop="username" 
            label="用户名" 
            width="150"
          />
          
          <el-table-column 
            prop="email" 
            label="邮箱" 
            width="200"
          />
          
          <el-table-column 
            prop="title" 
            label="邮件主题" 
            width="200"
          >
            <template #default="scope">
              <span class="font-medium text-gray-700">
                {{ scope.row.title }}
              </span>
            </template>
          </el-table-column>
          
          <el-table-column 
            prop="text" 
            label="消息内容"
            min-width="500"
          >
            <template #default="scope">
              <div class="p-2">
                <div class="text-gray-600 text-sm mb-2 line-clamp-2">
                  {{ stripHtmlTags(scope.row.text).length > 150 
                    ? stripHtmlTags(scope.row.text).slice(0, 150) + '...' 
                    : stripHtmlTags(scope.row.text) }}
                </div>
                <div class="flex items-center space-x-2">
                  <el-button 
                    type="text" 
                    size="small"
                    @click="openHtmlInNewWindow(scope.row.text)"
                    class="text-primary"
                  >
                    查看完整HTML内容
                  </el-button>
                  <el-button 
                    type="text" 
                    size="small"
                    @click="openEditDialog(scope.row, scope.$index)"
                    class="text-red-400 hover:text-red-600"
                  >
                    修改
                  </el-button>
                </div>
              </div>
            </template>
          </el-table-column>
          
          <el-table-column 
            label="状态" 
            width="120"
            align="center"
          >
            <template #default="scope">
              <el-tag 
                :type="scope.row.autoSent ? 'success' : scope.row.autoSentError ? 'danger' : 'info'"
                size="small"
              >
                {{
                  scope.row.autoSent ? '已生成' : 
                  scope.row.autoSentError ? '生成失败' : '未生成'
                }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </div>

      <!-- 参数输入区 -->
      <div class="flex flex-wrap items-center justify-center gap-4 my-6">
        <!-- 发送类型选择框 -->
        <el-select
          v-model="mode"
          placeholder="请选择发送类型"
          style="width: 180px"
          clearable
        >
          <el-option label="祝贺邮件" :value="0" />
          <el-option label="事件处理" :value="1" />
        </el-select>
        
        <!-- 选择模式选择框 -->
        <el-select
          v-model="selectMode"
          placeholder="请选择发送模式"
          style="width: 180px"
          clearable
        >
          <el-option label="遍历发送" :value="0" />
          <el-option label="指定用户发送" :value="1" />
        </el-select>
        
        <!-- 发送者输入框 -->
        <el-input
          v-model="sender"
          placeholder="请输入发送者名称"
          style="width: 180px"
        />
        <el-select 
        filterable 
        v-if="selectMode === 1"
        v-model="receiveUsername" 
        size="large" 
        placeholder="请选择接收者" 
        style="width: 220px;">
          <el-option v-for="item in options" :key="item.value" :label="item.label" :value="item.value" />
        </el-select>
        
        <!-- 接收者输入框 - 仅在指定用户发送模式下显示 -->
        <!-- <el-input
          v-if="selectMode === 1"
          v-model="receiveUsername"
          placeholder="请输入接收者名称"
          style="width: 220px"
        /> -->
        
        <!-- 仅生成文本/生成HTML开关 -->
        <el-switch
          v-model="onlyText"
          active-value="1"
          inactive-value="0"
          active-text="仅生成文本"
          inactive-text="生成HTML"
          class="mr-4"
        />
        
        <!-- 工作流请求按钮 -->
        <el-button 
          @click="executeWorkflow" 
          :disabled="isLoading || !isFormValid"
          type="primary"
          style="padding: 0 30px; height: 40px"
        >
          {{ isLoading ? '执行中...' : '发起工作流请求' }}
        </el-button>
      </div>

      <!-- 状态提示区 -->
      <div v-if="workflowResults.length === 0 && !isLoading" class="mt-4 p-6 text-center bg-white rounded-lg border border-gray-200">
        暂无数据，请输入参数并点击上方按钮发起请求
      </div>

      <div v-if="isLoading && workflowResults.length === 0" class="mt-4 p-6 text-center bg-white rounded-lg border border-gray-200">
        正在加载数据...
      </div>

      <div v-if="errorMessage" class="mt-4 p-4 bg-red-50 border border-red-200 rounded-md text-red-700 text-sm">
        错误：{{ errorMessage }}
      </div>
    </div>

    <!-- 编辑对话框 -->
    <el-dialog 
      v-model="editDialogVisible" 
      title="编辑邮件内容" 
      width="700px"
      :close-on-click-modal="false"
      append-to-body
    >
      <div class="space-y-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">邮件主题</label>
          <el-input 
            v-model="editingRow.title" 
            placeholder="请输入邮件主题"
          />
        </div>
        
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">邮件内容 (HTML格式)</label>
          <el-input 
            v-model="editingRow.text" 
            type="textarea"
            :rows="10"
            placeholder="请输入HTML格式的邮件内容"
            resize="none"
          />
        </div>
        
        <div v-if="editingRow.text" class="border border-gray-200 rounded-md p-3 mt-2">
          <label class="block text-sm font-medium text-gray-700 mb-1">内容预览</label>
          <div 
            class="p-3 bg-gray-50 rounded border border-gray-200 max-h-40 overflow-y-auto"
            ref="previewContainer"
          ></div>
        </div>
      </div>
      
      <template #footer>
        <div class="flex justify-end space-x-3">
          <el-button @click="editDialogVisible = false">取消</el-button>
          <el-button 
            type="primary" 
            @click="saveEditedRow"
            :loading="isSaving"
          >
            保存修改
          </el-button>
        </div>
      </template>
    </el-dialog>
  </div>
</template>

<script>
import { 
  ElTable, ElTableColumn, ElButton, ElInput, ElSelect, 
  ElOption, ElDialog, ElMessage, ElSwitch, ElTag 
} from 'element-plus'
import 'element-plus/dist/index.css'
import { getAllUser } from "@/api/user";

export default {
  components: {
    ElTable, ElTableColumn, ElButton, ElInput, ElSelect, 
    ElOption, ElDialog, ElSwitch, ElTag
  },
  props: {
    token: {
      type: String,
      required: true
    },
    receiveUserOptions: {
      type: Array,
      default: () => [
        { value: 'user1', label: '用户一' },
        { value: 'user2', label: '用户二' },
        { value: 'user3', label: '用户三' },
        { value: 'user4', label: '用户四' },
        { value: 'user5', label: '用户五' },
        { value: 'robot', label: '企微小助手' }
      ]
    }
  },
  data() {
    return {
      // API配置
      workflowUrl: import.meta.env.VITE_WORKFLOW_URL,
      apiKey: "app-aQ1uLzAwRibhwT8zGHaVZKLJ",
      
      // 输入参数
      ip: import.meta.env.VITE_API_URL,
      mode: null,          // 发送类型
      selectMode: null,    // 发送模式
      sender: '',          // 发送者名称
      receiveUsername: '', // 接收者名称
      onlyText: "0",       
      userId: "abc-123",   
      
      workflowResults: [],
      isLoading: false,
      errorMessage: null,
      
      // 编辑对话框相关
      editDialogVisible: false,
      editingRow: null,
      editingIndex: -1,
      isSaving: false,

      //
      options: [],
      sender: ''
    };
  },
  computed: {
    // 表单验证逻辑
    isFormValid() {
      const modeValid = this.mode !== null && this.mode !== '';
      const selectModeValid = this.selectMode !== null && this.selectMode !== '';
      const senderValid = this.sender.trim() !== '';
      
      // 当选择指定用户发送模式时，接收者为必填项
      const receiveUserValid = this.selectMode === 1 
        ? this.receiveUsername.trim() !== '' 
        : true;
      
      return modeValid && selectModeValid && senderValid && receiveUserValid;
    }
  },
  watch: {
    'editingRow.text': {
      handler(newValue) {
        this.renderEmailPreview(newValue);
      },
      immediate: true
    }
  },
  methods: {
    async getList() {
      const res = await getAllUser()


      if (res.status === 200) {
        ElMessage.success('用户事件获取成功')
      }
      this.options = res.data.items.map(item => {
        return {
          label: item.real_name,
          value: item.id
        }
      })
    },
    // 处理HTML标签
    stripHtmlTags(html) {
      if (!html) return '';
      return html.replace(/<[^>]*>?/gm, '');
    },
    
    // 格式化接收者名称，在每个名称前后添加*
    formatReceiveUsernames(input) {
      if (!input || input.trim() === '') return '';
      
      // 分割用户并过滤空值
      const users = input.split('、').filter(user => user.trim() !== '');
      
      // 为每个用户添加前后*
      const formattedUsers = users.map(user => `*${user.trim()}*`);
      
      // 重新组合
      return formattedUsers.join('、');
    },
    
    // 在新窗口打开HTML内容
    openHtmlInNewWindow(htmlContent) {
      try {
        const newWindow = window.open('', '_blank', 'width=1000,height=800,scrollbars=yes');
        if (!newWindow) {
          this.errorMessage = '浏览器阻止了弹出窗口，请允许弹出后重试';
          return;
        }
        
        newWindow.document.write(`
          <!DOCTYPE html>
          <html lang="zh-CN">
          <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>HTML内容预览</title>
            <style>
              body { 
                font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
                padding: 30px;
                max-width: 1200px;
                margin: 0 auto;
                line-height: 1.6;
              }
            </style>
          </head>
          <body>
            <div class="preview-content">${htmlContent}</div>
          </body>
          </html>
        `);
        newWindow.document.close();
      } catch (e) {
        this.errorMessage = `打开预览失败：${e.message}`;
        console.error('预览窗口错误：', e);
      }
    },
    
    // 打开编辑对话框
    openEditDialog(row, index) {
      this.editingRow = {
        ...row,
        originalText: row.text,
        originalTitle: row.title
      };
      this.editingIndex = index;
      this.editDialogVisible = true;
      this.$nextTick(() => {
        this.renderEmailPreview(row.text);
      });
    },

    // 渲染邮件预览
    renderEmailPreview(htmlContent) {
      const container = this.$refs.previewContainer;
      if (!container || !htmlContent) return;
      
      container.innerHTML = '';
      const shadowContainer = document.createElement('div');
      container.appendChild(shadowContainer);
      const shadowRoot = shadowContainer.attachShadow({ mode: 'open' });
      
      const previewDiv = document.createElement('div');
      previewDiv.innerHTML = htmlContent;
      
      const style = document.createElement('style');
      style.textContent = `
        body { font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; margin: 0; padding: 0; }
        * { box-sizing: border-box; }
      `;
      
      shadowRoot.appendChild(style);
      shadowRoot.appendChild(previewDiv);
    },
    
    // 保存编辑的内容
    saveEditedRow() {
      if (!this.editingRow || this.editingIndex === -1) return;
      
      const hasChanged = this.editingRow.text !== this.editingRow.originalText || 
                         this.editingRow.title !== this.editingRow.originalTitle;
      
      if (!hasChanged) {
        ElMessage.info('内容未发生变化');
        this.editDialogVisible = false;
        return;
      }
      
      this.isSaving = true;
      setTimeout(() => {
        this.workflowResults[this.editingIndex].text = this.editingRow.text;
        this.workflowResults[this.editingIndex].title = this.editingRow.title;
        
        ElMessage.success('修改已保存');
        this.isSaving = false;
        this.editDialogVisible = false;
      }, 800);
    },
    
    // 执行工作流
    async executeWorkflow() {
      if (!this.isFormValid) {
        this.errorMessage = "请填写所有必填参数";
        return;
      }
      
      this.isLoading = true;
      this.workflowResults = [];
      this.errorMessage = null;
      
      // 构造输入参数
      const inputData = {
        token: this.token,
        ip: this.ip,
        mode: Number(this.mode),
        select_mode: Number(this.selectMode),
        sender: this.sender.trim(),
        only_text: Number(this.onlyText)
      };
      
      // 当选择指定用户发送模式时，添加格式化后的接收者参数
      if (this.selectMode === 1) {
        inputData.receive_username = this.formatReceiveUsernames(this.receiveUsername);
      }
      
      try {
        const response = await fetch(this.workflowUrl, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${this.apiKey}`,
            'Content-Type': 'application/json'
          },
          body: JSON.stringify({
            inputs: inputData,
            response_mode: "streaming",
            user: this.userId
          })
        });
        
        if (!response.ok) {
          if (response.status === 404) throw new Error("请求地址不存在");
          if (response.status === 401) throw new Error("认证失败，请检查API Key");
          if (response.status === 400) {
            const errorDetail = await response.text();
            throw new Error(`请求参数错误: ${errorDetail.substring(0, 200)}`);
          }
          throw new Error(`请求失败 (${response.status})`);
        }
        
        const reader = response.body.getReader();
        const decoder = new TextDecoder();
        let buffer = '';
        
        while (true) {
          const { done, value } = await reader.read();
          if (done) break;
          
          buffer += decoder.decode(value, { stream: true });
          const lines = buffer.split('\n');
          buffer = lines.pop() || '';
          
          lines.forEach(line => {
            const decodedLine = line.trim();
            if (!decodedLine || decodedLine === "[DONE]") return;
            
            if (decodedLine.startsWith("data: ")) {
              try {
                const eventData = JSON.parse(decodedLine.slice(6));
                // 仅处理 node_finished 事件且 title 为 '输出汇总' 的响应
                if (eventData.event === 'node_finished' && eventData.data?.title === '输出汇总') {
                  const { data } = eventData;
                  const outputs = data.outputs || {};
                  
                  const newRow = {
                    user_id: outputs.user_id || '',
                    username: outputs.username || '',
                    email: outputs.email || '',
                    title: outputs.title || '',
                    text: outputs.text || '',
                    autoSent: false,
                    autoSentError: false
                  };
                  
                  this.workflowResults.push(newRow);
                }
                else if (eventData.event === 'workflow_finished') {
                }
              } catch (e) {
                console.error('解析失败:', e);
              }
            }
          });
        }
      } catch (error) {
        this.errorMessage = error.message;
      } finally {
        this.isLoading = false;
      }
    }
  },
  mounted() {
    this.getList()
  }
};
</script>

<style scoped>
.line-clamp-2 {
  display: -webkit-box;      
  -webkit-line-clamp: 2;     
  line-clamp: 2;             
  -webkit-box-orient: vertical;
  overflow: hidden;
  text-overflow: ellipsis;
}

.text-primary {
  color: #409eff;
}

.text-red-400 {
  color: #f87171;
}

.text-red-400:hover {
  color: #ef4444;
}

.main-title {
  font-size: 3rem !important;
  font-weight: bold !important;
  color: #1f2937 !important;
}

.page-container {
  background-color: #f9fafb !important;
}

:deep(.el-table--border) {
  border: 1px solid #e5e7eb;
}

:deep(.el-table th) {
  background-color: #f9fafb;
}

:deep(.el-input__wrapper),
:deep(.el-cascader__wrapper) {
  height: 40px;
}

:deep(.el-select .el-input__wrapper) {
  height: 40px;
  display: flex;
  align-items: center;
}
</style>