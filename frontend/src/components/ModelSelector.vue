<template>
  <div class="model-selector">
    <div class="model-type-selector">
      <label>模型类型:</label>
      <select v-model="selectedModelType" @change="onModelTypeChange">
        <option value="">选择模型类型</option>
        <option v-for="(typeInfo, typeKey) in modelTypes" :key="typeKey" :value="typeKey">
          {{ typeInfo.name }}
        </option>
      </select>
    </div>
    
    <div class="model-name-selector" v-if="selectedModelType && availableModels.length > 0">
      <label>具体模型:</label>
      <select v-model="selectedModelName">
        <option value="">使用默认模型</option>
        <option v-for="model in availableModels" :key="model" :value="model">
          {{ model }}
        </option>
      </select>
    </div>
    
    <div class="temperature-selector">
      <label>温度参数 ({{ temperature }}):</label>
      <input 
        type="range" 
        min="0" 
        max="1" 
        step="0.1" 
        v-model="temperature"
        class="temperature-slider"
      >
      <div class="temperature-labels">
        <span>保守</span>
        <span>创新</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import api from '../api'

// Props
const props = defineProps({
  modelValue: {
    type: Object,
    default: () => ({
      model_type: 'local',
      model_name: '',
      temperature: 0.5
    })
  }
})

// Emits
const emit = defineEmits(['update:modelValue'])

// Reactive data
const modelTypes = ref({})
const selectedModelType = ref(props.modelValue.model_type || 'local')
const selectedModelName = ref(props.modelValue.model_name || '')
const temperature = ref(props.modelValue.temperature || 0.5)

// Computed
const availableModels = computed(() => {
  if (!selectedModelType.value || !modelTypes.value[selectedModelType.value]) {
    return []
  }
  return modelTypes.value[selectedModelType.value].models || []
})

// Methods
const fetchModelTypes = async () => {
  try {
    const response = await api.get('/chat/models')
    if (response.status === 200) {
      modelTypes.value = response.data.model_types
    }
  } catch (error) {
    console.error('获取模型类型失败:', error)
    // 提供默认的模型类型
    modelTypes.value = {
      local: {
        name: '本地模型 (Ollama)',
        description: '使用本地部署的Ollama模型',
        models: ['deepseek-r1:8b']
      },
      cloud: {
        name: '云端模型 (DeepSeek)',
        description: '使用DeepSeek云端API',
        models: ['deepseek-chat', 'deepseek-coder']
      }
    }
  }
}

const onModelTypeChange = () => {
  // 当模型类型改变时，重置模型名称
  selectedModelName.value = ''
  updateModelValue()
}

const updateModelValue = () => {
  const newValue = {
    model_type: selectedModelType.value,
    model_name: selectedModelName.value,
    temperature: parseFloat(temperature.value)
  }
  emit('update:modelValue', newValue)
}

// Watchers
watch([selectedModelType, selectedModelName, temperature], () => {
  updateModelValue()
})

// Lifecycle
onMounted(() => {
  fetchModelTypes()
})
</script>

<style scoped>
.model-selector {
  background: #f8f9fa;
  border: 1px solid #e9ecef;
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1rem;
}

.model-type-selector,
.model-name-selector,
.temperature-selector {
  margin-bottom: 1rem;
}

.model-type-selector:last-child,
.model-name-selector:last-child,
.temperature-selector:last-child {
  margin-bottom: 0;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 500;
  color: #333;
}

select {
  width: 100%;
  padding: 0.5rem;
  border: 1px solid #ddd;
  border-radius: 4px;
  font-size: 0.9rem;
}

.temperature-slider {
  width: 100%;
  margin: 0.5rem 0;
}

.temperature-labels {
  display: flex;
  justify-content: space-between;
  font-size: 0.8rem;
  color: #666;
}

select:focus,
.temperature-slider:focus {
  outline: none;
  border-color: #2196F3;
  box-shadow: 0 0 0 2px rgba(33, 150, 243, 0.2);
}
</style>
