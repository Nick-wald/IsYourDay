<script setup>
import {
  Download, ChatLineSquare, Notebook, Link,
  Picture, List, View, FullScreen, Document, Close
} from '@element-plus/icons-vue'
import { marked } from 'marked'
import { onMounted, ref,watch } from 'vue'
import DOMPurify from 'dompurify'
import { uploadFile } from '@/api/file'
import { ApiBaseURL } from '@/utils/authUtils'

const props = defineProps({
  modelValue: {
    type: String,
    required: true
  },
  type: {
    type: String,
    required: true
  }
})

const emit = defineEmits(['update:modelValue']);
const markdownContent = ref(props.modelValue)
const isPreview = ref(false)

const apiURL = ApiBaseURL

marked.setOptions({
  breaks: true, // 将回车转换为 <br>
  gfm: true, // 启用 GitHub 风格的 Markdown
  // sanitize: false, // 允许HTML标签
})

// const uploadImg = async () => {
  
// }

const handleFile = async (e) => {
  const form = new FormData()
  form.append('files', e.target.files[0])
  form.append('is_public', true)
  form.append('use_streaming', true)
  const res = await uploadFile(form)
  const file_id = res.data.uploaded_files[0].id
  const img = `${apiURL}/file/${file_id}/stream`

  const textarea = document.querySelector('.textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = markdownContent.value.substring(start, end)

  let insertion = `![在这里写图片描述](${img})`
  const newContent =
    markdownContent.value.substring(0, start) +
    insertion +
    markdownContent.value.substring(end)

  markdownContent.value = newContent
  content()
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + insertion.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  }, 0)
}

const insertMarkdown = (type) => {
  const textarea = document.querySelector('.textarea')
  if (!textarea) return

  const start = textarea.selectionStart
  const end = textarea.selectionEnd
  const selected = markdownContent.value.substring(start, end)

  let insertion = ''

  switch (type) {
    case 'bold':
      insertion = `**${selected || '粗体文本'}**`
      break
    case 'italic':
      insertion = `*${selected || '斜体文本'}*`
      break
    case 'heading':
      insertion = `\n## ${selected || '标题'}\n`
      break
    case 'link':
      insertion = `[${selected || '链接文本'}](https://example.com)`
      break
    case 'list':
      insertion = `\n1.  ${selected || '列表项'}\n2.  列表项\n3.  列表项\n`
      break
    case 'quote':
      insertion = `\n> ${selected || '引用文本'}\n`
      break
    case 'code':
      insertion = selected ?
        `\`\`\`\n${selected}\n\`\`\`` :
        `\`\`\`\n代码块\n\`\`\``
      break
    case 'image':
      insertion = `![${selected || '图片描述'}](https://example.com/image.jpg)`
      break
    default:
      return
  }

  const newContent =
    markdownContent.value.substring(0, start) +
    insertion +
    markdownContent.value.substring(end)

  markdownContent.value = newContent
  content()
  setTimeout(() => {
    textarea.focus()
    const newCursorPos = start + insertion.length
    textarea.setSelectionRange(newCursorPos, newCursorPos)
  }, 0)
}

const content = () => {
  let text = ''
  if(props.type) {
    text = DOMPurify.sanitize(marked(markdownContent.value))
  }
  else {
    text = markdownContent.value
  }
  // const text = DOMPurify.sanitize(marked(markdownContent.value))
  document.querySelector('.show-area .show-card').innerHTML = text
  emit('update:modelValue', markdownContent.value)
  // showContent.value = text
}

const togglePreview = () => {
  isPreview.value = !isPreview.value
}

watch(markdownContent, () => {
  content()
})

watch(() => props.modelValue, (newVal) => {
  markdownContent.value = newVal
  content()
})
onMounted(() => {
  content()
})
</script>

<template>
  <div class="edit-container">
    <div class="tool-bar">
      <el-button-group>
        <el-button size="small" @click="insertMarkdown('heading')" title="标题">
          <strong>H</strong>
        </el-button>
        <el-button size="small" @click="insertMarkdown('bold')" title="加粗">
          <strong>B</strong>
        </el-button>
        <el-button size="small" @click="insertMarkdown('italic')" title="斜体">
          <em>I</em>
        </el-button>
        <el-button size="small" @click="insertMarkdown('quote')" title="引用">
          <el-icon>
            <ChatLineSquare />
          </el-icon>
        </el-button>
        <el-button size="small" @click="insertMarkdown('code')" title="代码">
          <el-icon>
            <Notebook />
          </el-icon>
        </el-button>
        <el-button size="small" @click="insertMarkdown('link')" title="链接">
          <el-icon>
            <Link />
          </el-icon>
        </el-button>
        <el-button size="small" @click="insertMarkdown('image')" title="图片">
          <el-icon>
            <Picture />
          </el-icon>
        </el-button>
        <el-button size="small" @click="insertMarkdown('list')" title="列表">
          <el-icon>
            <List />
          </el-icon>
        </el-button>
        <label>
          <div class="el-button el-button--small" style="transform: translateY(-2px);margin-left: 1px;">
            上传
          </div>
          <input style="display: none;" type="file" @change="handleFile">
        </label>
      </el-button-group>

      <!-- 预览控制 -->
      <el-button-group>
        <el-button size="small" @click="togglePreview" title="预览模式" :type="isPreview ? 'primary' : ''"
          class="preview-button">
          <el-icon>
            <View />
          </el-icon>
          预览
        </el-button>
      </el-button-group>
    </div>
    <div :class="{'edit-area': true, 'pre-edit-area': isPreview}">
      <textarea @input="content" class="textarea" v-model="markdownContent"></textarea>
    </div>
    <div :class="{'show-area': true,'pre-show-area': isPreview}">
      <div class="show-card"></div>
    </div>
  </div>
</template>

<style scoped>
.edit-container {
  width: 100%;
  /* height: 500px;  */
  /* background-color: aliceblue; */
  border: 1px solid #ccc;
  border-radius: 8px;
}
.edit-container::after{
  content: "";
  display: block;
  clear: both;
}

.tool-bar {
  width: 100%;
  /* height: 80px; */
  padding: 5px 10px;
  background-color: hwb(196 94% 2%);
  box-sizing: border-box;
  border-bottom: 1px solid #ccc;
  border-top-left-radius: 8px;
  border-top-right-radius: 8px;
}

.edit-area{
  float: left;
  width: 50%;
  /* background-color: aqua; */
  height: 400px;
  padding: 8px;
  box-sizing: border-box;
}
.pre-edit-area{
  display: none;
}
.edit-area .textarea{
  width: 100%;
  height: 100%;
  border: 1px solid #ccc;
  border-radius: 6px;
  box-sizing: border-box;
  outline: none;
  padding: 8px;
  resize: none;
}

.show-area{
  float: left;
  width: 50%;
  height: 400px;
  /* background-color: blanchedalmond; */
  box-sizing: border-box;
  padding: 8px;
}
.pre-show-area{
  width: 100%;
}
.show-area .show-card{
  width: 100%;
  height: 100%;
  /* background-color: aliceblue; */
  border-radius: 6px;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  padding: 5px 8px;
  word-break: break-all;
  box-sizing: border-box;
}

@media (max-width: 768px) {
  .edit-container{
    display: flex;
    flex-direction: column;
  }

  .edit-area{
    width: 100%;
    height: 160px;
  }

  .show-area{
    width: 100%;
    height: 240px;
    order: -1;
  }
}

</style>