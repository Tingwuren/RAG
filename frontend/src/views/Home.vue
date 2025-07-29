<template>
  <div class="home-container">
    <NavBar />
    <div class="main-content">
      <div class="sidebar">
        <div class="menu-item" :class="{ active: activeTab === 'chat' }" @click="activeTab = 'chat'">
          普通对话
        </div>
        <div class="menu-item" :class="{ active: activeTab === 'knowledge' }" @click="activeTab = 'knowledge'">
          知识库对话
        </div>
        <div class="menu-item" :class="{ active: activeTab === 'dialect' }" @click="activeTab = 'dialect'">
          方言对话
        </div>
        <div class="menu-item" :class="{ active: activeTab === 'manage' }" @click="activeTab = 'manage'">
          知识库管理
        </div>
      </div>
      <div class="content">
        <div v-if="activeTab === 'chat'" class="chat-container">
          <ModelSelector v-model="modelConfig" />
          <div class="chat-messages" ref="messagesContainer">
            <div v-for="(message, index) in messages" :key="index" :class="['message', message.type]">
              <div v-if="message.type === 'bot'" v-html="formatMessage(message.content)"></div>
              <div v-else>{{ message.content }}</div>
            </div>
          </div>
          <div class="chat-input">
            <input v-model="userInput" @keyup.enter="!isLoading && sendMessage" placeholder="输入消息...">
            <button @click="sendMessage" :disabled="isLoading">{{isLoading ? '生成中...' : '发送'}}</button>
          </div>
        </div>

        <div v-else-if="activeTab === 'knowledge'" class="knowledge-chat-container">
          <div class="knowledge-selector">
            <select v-model="selectedKnowledge">
              <option value="">选择知识库</option>
              <option v-for="kb in knowledgeBases" :key="kb" :value="kb">{{ kb }}</option>
            </select>
          </div>
          <ModelSelector v-model="knowledgeModelConfig" />
          <div class="chat-messages" ref="knowledgeMessagesContainer">
            <div v-for="(message, index) in knowledgeMessages" :key="index" :class="['message', message.type]">
              <div v-if="message.type === 'bot'" v-html="formatMessage(message.content)"></div>
              <div v-else>{{ message.content }}</div>
            </div>
          </div>
          <div class="chat-input">
            <input v-model="knowledgeInput" @keyup.enter="!isKnowledgeLoading && sendKnowledgeMessage" placeholder="输入消息...">
            <button @click="sendKnowledgeMessage" :disabled="isKnowledgeLoading">{{isKnowledgeLoading ? '生成中...' : '发送'}}</button>
          </div>
        </div>

        <div v-else-if="activeTab === 'dialect'" class="dialect-chat-container">
          <ModelSelector v-model="dialectModelConfig" />
          <div class="chat-messages" ref="dialectMessagesContainer">
            <div v-for="(message, index) in dialectMessages" :key="index" :class="['message', message.type]">
              <div v-if="message.type === 'bot'" v-html="formatMessage(message.content)"></div>
              <div v-else>{{ message.content }}</div>
            </div>
          </div>
          <div class="chat-input">
            <input v-model="dialectInput" @keyup.enter="!isDialectLoading && sendDialectMessage" placeholder="输入消息...">
            <button @click="sendDialectMessage" :disabled="isDialectLoading">{{isDialectLoading ? '生成中...' : '发送'}}</button>
          </div>
        </div>

        <div v-else-if="activeTab === 'manage'" class="knowledge-management">
          <div class="create-knowledge">
            <h3>创建知识库</h3>
            <input v-model="newKnowledgeName" placeholder="输入知识库名称">
            <button @click="createKnowledge">创建</button>
          </div>
          
          <div class="delete-knowledge">
            <h3>删除知识库</h3>
            <select v-model="deleteKnowledgeName">
              <option value="">选择知识库</option>
              <option v-for="kb in filteredKnowledgeBases" :key="kb" :value="kb">{{ kb }}</option>
            </select>
            <button @click="deleteKnowledge" class="delete-btn">删除</button>
          </div>
          
          <div class="upload-file">
            <h3>上传文件</h3>
            <select v-model="uploadKnowledgeName">
              <option value="">选择知识库</option>
              <option v-for="kb in filteredKnowledgeBases" :key="kb" :value="kb">{{ kb }}</option>
            </select>
            <input type="file" @change="handleFileUpload" accept=".pdf">
            <button @click="uploadFile" :disabled="!selectedFile">上传</button>
          </div>
          <div class="process-files">
            <h3>处理文件</h3>
            <select v-model="processKnowledgeName">
              <option value="">选择知识库</option>
              <option v-for="kb in filteredKnowledgeBases" :key="kb" :value="kb">{{ kb }}</option>
            </select>
            <button @click="processFiles">处理</button>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue'
import NavBar from '../components/NavBar.vue'
import ModelSelector from '../components/ModelSelector.vue'
import api from '../api'
import MarkdownIt from 'markdown-it'

const md = new MarkdownIt()
const activeTab = ref('chat')
const userInput = ref('')
const knowledgeInput = ref('')
const dialectInput = ref('')
const messages = ref([])
const knowledgeMessages = ref([])
const dialectMessages = ref([])
const knowledgeBases = ref([])
const selectedKnowledge = ref('')
const newKnowledgeName = ref('')
const uploadKnowledgeName = ref('')
const processKnowledgeName = ref('')
const selectedFile = ref(null)
const deleteKnowledgeName = ref('')
const isLoading = ref(false)
const isKnowledgeLoading = ref(false)
const isDialectLoading = ref(false)

// 模型选择相关
const modelConfig = ref({
  model_type: 'local',
  model_name: '',
  temperature: 0.5
})
const knowledgeModelConfig = ref({
  model_type: 'cloud',
  model_name: '',
  temperature: 0.5
})
const dialectModelConfig = ref({
  model_type: 'cloud',
  model_name: '',
  temperature: 0.5
})

// 获取知识库列表
const fetchKnowledgeBases = async () => {
  try {
    const response = await api.get('/knowledge/list')
    if (response.status === 200) {
      knowledgeBases.value = response.data.knowledge_bases
    }
  } catch (error) {
    console.error('获取知识库列表失败:', error)
    // 如果接口调用失败，提供一些样例数据
    knowledgeBases.value = ['示例知识库1', '示例知识库2']
  }
}

// 发送普通消息
const sendMessage = async () => {
  if (!userInput.value.trim()) return

  messages.value.push({ type: 'user', content: userInput.value })

  // 添加加载状态
  isLoading.value = true
  // 添加临时的"正在生成"消息
  const loadingMsgIndex = messages.value.length
  messages.value.push({ type: 'loading', content: '正在思考，请稍候...' })

  try {
    const requestData = {
      query: userInput.value,
      model_type: modelConfig.value.model_type,
      model_name: modelConfig.value.model_name,
      temperature: modelConfig.value.temperature
    }
    const response = await api.post('/chat/', requestData)
    // 移除加载消息
    messages.value.splice(loadingMsgIndex, 1)
    messages.value.push({ type: 'bot', content: response.data.response })
  } catch (error) {
    console.error('发送消息失败:', error)
    // 移除加载消息
    messages.value.splice(loadingMsgIndex, 1)
    messages.value.push({ type: 'error', content: '发送消息失败，请重试' })
  } finally {
    isLoading.value = false
  }
  userInput.value = ''
}

// 发送知识库消息
const sendKnowledgeMessage = async () => {
  if (!knowledgeInput.value.trim() || !selectedKnowledge.value) return

  knowledgeMessages.value.push({ type: 'user', content: knowledgeInput.value })

  // 添加加载状态
  isKnowledgeLoading.value = true
  // 添加临时的"正在生成"消息
  const loadingMsgIndex = knowledgeMessages.value.length
  knowledgeMessages.value.push({ type: 'loading', content: '正在从知识库搜索信息，请稍候...' })

  try {
    const requestData = {
      knowledge_name: selectedKnowledge.value,
      query: knowledgeInput.value,
      model_type: knowledgeModelConfig.value.model_type,
      model_name: knowledgeModelConfig.value.model_name,
      temperature: knowledgeModelConfig.value.temperature
    }
    const response = await api.post('/chat/with-knowledge', requestData)
    // 移除加载消息
    knowledgeMessages.value.splice(loadingMsgIndex, 1)
    knowledgeMessages.value.push({ type: 'bot', content: response.data.response })
  } catch (error) {
    console.error('发送消息失败:', error)
    // 移除加载消息
    knowledgeMessages.value.splice(loadingMsgIndex, 1)
    knowledgeMessages.value.push({ type: 'error', content: '发送消息失败，请重试' })
  } finally {
    isKnowledgeLoading.value = false
  }
  knowledgeInput.value = ''
}

// 发送方言消息
const sendDialectMessage = async () => {
  if (!dialectInput.value.trim()) return

  dialectMessages.value.push({ type: 'user', content: dialectInput.value })

  // 添加加载状态
  isDialectLoading.value = true
  // 添加临时的"正在生成"消息
  const loadingMsgIndex = dialectMessages.value.length
  dialectMessages.value.push({ type: 'loading', content: '正在处理方言信息，请稍候...' })

  try {
    const requestData = {
      query: dialectInput.value,
      model_type: dialectModelConfig.value.model_type,
      model_name: dialectModelConfig.value.model_name,
      temperature: dialectModelConfig.value.temperature
    }
    const response = await api.post('/chat/with-dialect-knowledge', requestData)
    // 移除加载消息
    dialectMessages.value.splice(loadingMsgIndex, 1)
    dialectMessages.value.push({ type: 'bot', content: response.data.response })
  } catch (error) {
    console.error('发送消息失败:', error)
    // 移除加载消息
    dialectMessages.value.splice(loadingMsgIndex, 1)
    dialectMessages.value.push({ type: 'error', content: '发送消息失败，请重试' })
  } finally {
    isDialectLoading.value = false
  }
  dialectInput.value = ''
}

// 创建知识库
const createKnowledge = async () => {
  if (!newKnowledgeName.value.trim()) return
  
  try {
    await api.post('/knowledge/create', {
      knowledge_name: newKnowledgeName.value
    })
    knowledgeBases.value.push(newKnowledgeName.value)
    newKnowledgeName.value = ''
    alert('知识库创建成功')
  } catch (error) {
    console.error('创建知识库失败:', error)
    alert('创建知识库失败，请重试')
  }
}

// 删除知识库
const deleteKnowledge = async () => {
  if (!deleteKnowledgeName.value) return
  
  if (!confirm(`确定要删除知识库 "${deleteKnowledgeName.value}" 吗？此操作不可恢复！`)) {
    return
  }
  
  try {
    const response = await api.post('/knowledge/delete', {
      knowledge_name: deleteKnowledgeName.value
    })
    
    // 从列表中移除已删除的知识库
    knowledgeBases.value = knowledgeBases.value.filter(kb => kb !== deleteKnowledgeName.value)
    deleteKnowledgeName.value = ''
    alert('知识库删除成功')
  } catch (error) {
    console.error('删除知识库失败:', error)
    alert('删除知识库失败，请重试')
  }
}

// 处理文件上传
const handleFileUpload = (event) => {
  selectedFile.value = event.target.files[0]
}

// 上传文件
const uploadFile = async () => {
  if (!selectedFile.value || !uploadKnowledgeName.value) return
  
  const formData = new FormData()
  formData.append('file', selectedFile.value)
  formData.append('knowledge_name', uploadKnowledgeName.value)
  
  try {
    await api.post('/knowledge/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data'
      }
    })
    alert('文件上传成功')
    selectedFile.value = null
  } catch (error) {
    console.error('上传文件失败:', error)
    alert('上传文件失败，请重试')
  }
}

// 处理文件
const processFiles = async () => {
  if (!processKnowledgeName.value) return
  
  try {
    await api.post('/knowledge/process', {
      knowledge_name: processKnowledgeName.value
    })
    alert('文件处理成功')
  } catch (error) {
    console.error('处理文件失败:', error)
    alert('处理文件失败，请重试')
  }
}

// 添加计算属性，过滤掉默认知识库
const filteredKnowledgeBases = computed(() => {
  return knowledgeBases.value.filter(kb => kb !== 'defualt');
})

// 格式化消息内容，支持Markdown
const formatMessage = (content) => {
  // 移除<think>标签及其内容
  let formattedContent = content;
  const thinkPattern = /<think>[\s\S]*?<\/think>/;
  formattedContent = formattedContent.replace(thinkPattern, '');
  
  return md.render(formattedContent.trim());
}

onMounted(() => {
  fetchKnowledgeBases()
  
  // 添加初始欢迎消息
  messages.value.push({ 
    type: 'bot', 
    content: '你好！我是你的智能助手。有什么我可以帮助你的吗？' 
  })
  
  knowledgeMessages.value.push({ 
    type: 'bot', 
    content: '欢迎使用知识库对话功能！\n\n请先从上方选择一个知识库，然后输入你的问题，我会根据知识库内容为你解答。' 
  })
  
  dialectMessages.value.push({ 
    type: 'bot', 
    content: '欢迎使用蒲仙话方言对话功能！\n\n你可以向我询问蒲仙话相关的问题，例如：\n- "祖父怎么说？"\n- "阿公是什么意思？"\n- "阿公的江口发音是什么？"\n\n我会尽力为你解答方言相关的疑问。' 
  })
})
</script>

<style scoped>
/* 容器和布局 */
.home-container {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  width: 100%;
  overflow-x: hidden;
}

.main-content {
  display: flex;
  flex: 1;
  margin-top: 4rem; /* 为固定导航栏留出空间 */
  width: 100%;
}

.content {
  flex: 1;
  padding: 1rem;
  overflow-y: auto;
  position: relative;
  height: calc(100vh - 4rem);
}

/* 侧边栏样式 */
.sidebar {
  width: 220px;
  background-color: #f8f9fa;
  border-right: 1px solid #e9ecef;
  display: flex;
  flex-direction: column;
  height: calc(100vh - 4rem); /* 减去导航栏的高度 */
  overflow-y: auto; /* 允许侧边栏滚动 */
  padding: 1.5rem 0;
  box-shadow: 0 0 10px rgba(0, 0, 0, 0.05);
}

.menu-item {
  padding: 1rem 1.5rem;
  cursor: pointer;
  transition: all 0.3s ease;
  text-align: left;
  border-left: 4px solid transparent;
  margin-bottom: 0.5rem;
  font-size: 1.05rem;
  display: flex;
  align-items: center;
  position: relative;
  overflow: hidden;
}

.menu-item:before {
  content: '';
  position: absolute;
  left: 0;
  bottom: 0;
  height: 1px;
  width: 85%;
  margin-left: 7.5%;
  background-color: #f0f0f0;
}

.menu-item:last-child:before {
  display: none;
}

.menu-item:hover {
  background-color: #edf2f7;
  border-left-color: #9bbde6;
  color: #3182ce;
}

.menu-item.active {
  background-color: #3498db;
  color: white;
  border-left-color: #2980b9;
  box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
}

.menu-item:after {
  content: '►';
  opacity: 0;
  margin-left: auto;
  font-size: 0.75rem;
  transition: opacity 0.3s ease;
}

.menu-item:hover:after {
  opacity: 0.5;
}

.menu-item.active:after {
  opacity: 1;
}

/* 聊天容器样式 */
.chat-container,
.knowledge-chat-container,
.dialect-chat-container {
  display: flex;
  flex-direction: column;
  height: calc(100vh - 4rem);
  width: 100%;
  position: relative;
}

.chat-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1rem;
  background-color: #f9f9f9;
  border-radius: 4px;
  margin-bottom: 70px; /* 为固定在底部的输入框留出空间 */
}

.message {
  margin-bottom: 1rem;
  padding: 0.8rem;
  border-radius: 4px;
  max-width: 80%;
}

.message.user {
  background-color: #e3f2fd;
  margin-left: auto;
}

.message.bot {
  background-color: #f5f5f5;
  margin-right: auto;
}

.message.error {
  background-color: #ffebee;
  color: #c62828;
}

.message.loading {
  background-color: #f0f8ff;
  color: #666;
  margin-right: auto;
  position: relative;
  padding-left: 2.5rem;
}

.message.loading:before {
  content: "";
  position: absolute;
  left: 0.8rem;
  top: calc(50% - 0.5rem);
  width: 1rem;
  height: 1rem;
  border: 3px solid #4b9cdb;
  border-radius: 50%;
  border-top-color: transparent;
  animation: spin 1s linear infinite;
}

@keyframes spin {
  0% { transform: rotate(0deg); }
  100% { transform: rotate(360deg); }
}

/* 输入框样式 */
.chat-input {
  display: flex;
  position: fixed;
  bottom: 0;
  left: 220px;
  width: calc(100% - 220px);
  padding: 1rem;
  box-sizing: border-box;
  background-color: white;
  border-top: 1px solid #ddd;
  z-index: 10;
}

.chat-input input {
  flex: 1;
  padding: 0.8rem 1rem;
  font-size: 1.1rem;
  height: 50px;
  border: 1px solid #ddd;
  border-radius: 4px;
}

.chat-input button {
  margin-left: 0.5rem;
  padding: 0.8rem 1.5rem;
  font-size: 1.1rem;
  height: 50px;
}

/* 知识库管理样式 */
.knowledge-management {
  display: flex;
  flex-direction: column;
  gap: 2rem;
}

.create-knowledge,
.delete-knowledge,
.upload-file,
.process-files,
.knowledge-selector {
  padding: 1rem;
  background-color: white;
  border-radius: 8px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
  margin-bottom: 1rem;
}

h3 {
  margin-bottom: 1rem;
  color: #333;
}

/* 表单元素样式统一 */
.create-knowledge input,
.delete-knowledge select,
.upload-file select,
.process-files select,
.knowledge-selector select,
.upload-file input[type="file"] {
  width: 100%;
  padding: 0.8rem 1rem;
  font-size: 1.1rem;
  height: 50px;
  border: 1px solid #ddd;
  border-radius: 4px;
  margin-bottom: 1rem;
}

/* 按钮样式 */
button {
  padding: 0.8rem 1.5rem;
  background-color: #2196F3;
  color: white;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  transition: background-color 0.3s;
}

button:hover {
  background-color: #1976D2;
}

button:disabled {
  background-color: #ccc;
  cursor: not-allowed;
}

.delete-btn {
  background-color: #f44336;
}

.delete-btn:hover {
  background-color: #d32f2f;
}

/* 响应式布局 */
@media screen and (max-width: 768px) {
  .sidebar {
    width: 120px;
    padding: 1rem 0;
  }
  
  .menu-item {
    padding: 0.8rem 1rem;
    font-size: 0.9rem;
  }
  
  .chat-input {
    left: 120px;
    width: calc(100% - 120px);
  }
}

/* 禁用发送按钮的样式 */
.chat-input button:disabled {
  background-color: #b0bec5;
  cursor: not-allowed;
  opacity: 0.7;
}

/* Markdown样式 */
:deep(ul), :deep(ol) {
  padding-left: 2rem;
  margin-bottom: 1rem;
}

:deep(li) {
  margin-bottom: 0.5rem;
}

:deep(p) {
  margin-bottom: 0.75rem;
}

:deep(code) {
  background-color: #f0f0f0;
  padding: 0.2rem 0.4rem;
  border-radius: 3px;
  font-family: monospace;
}

:deep(pre) {
  background-color: #f8f8f8;
  padding: 1rem;
  border-radius: 4px;
  overflow-x: auto;
  margin-bottom: 1rem;
}

:deep(blockquote) {
  border-left: 4px solid #ddd;
  padding-left: 1rem;
  color: #666;
  margin-bottom: 1rem;
}
</style>

<style>
/* 全局样式 */
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body {
  height: 100%;
  width: 100%;
  overflow-x: hidden;
}
</style> 