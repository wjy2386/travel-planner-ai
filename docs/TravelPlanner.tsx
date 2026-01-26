/**
 * 旅行规划Agent - Lovable前端集成组件
 * 
 * 使用方法：
 * 1. 将此文件复制到Lovable项目的components目录
 * 2. 确保后端API服务运行在 http://localhost:8000
 * 3. 在页面中引入并使用
 */

import React, { useState, useEffect, useRef } from 'react';
import ReactMarkdown from 'react-markdown';

// API配置
const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

interface PlanRequest {
  user_input: string;
  session_id?: string;
}

interface ApiResponse {
  success: boolean;
  message: string;
  data?: {
    itinerary: string;
    session_id: string;
    stage: string;
  };
  error?: string;
}

interface StreamEvent {
  type: 'start' | 'stage' | 'progress' | 'complete' | 'error';
  message?: string;
  stage?: string;
  progress?: number;
  data?: string;
  error?: string;
}

export default function TravelPlanner() {
  const [userInput, setUserInput] = useState('');
  const [result, setResult] = useState('');
  const [loading, setLoading] = useState(false);
  const [useStream, setUseStream] = useState(true);
  const [currentStage, setCurrentStage] = useState('');
  const [progress, setProgress] = useState(0);
  const [sessionId, setSessionId] = useState('');
  const [error, setError] = useState('');
  const resultRef = useRef<HTMLDivElement>(null);

  // 初始化会话ID
  useEffect(() => {
    const savedSessionId = localStorage.getItem('travel_session_id');
    if (savedSessionId) {
      setSessionId(savedSessionId);
    } else {
      const newSessionId = `session_${Date.now()}`;
      setSessionId(newSessionId);
      localStorage.setItem('travel_session_id', newSessionId);
    }
  }, []);

  // 滚动到结果区域
  useEffect(() => {
    if (result && resultRef.current) {
      resultRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [result]);

  // 获取阶段名称
  const getStageName = (stage: string): string => {
    const stageMap: Record<string, string> = {
      'analysis': '📊 分析需求',
      'planning': '🗺️ 规划行程',
      'validation': '✅ 校验可行性',
      'delivery': '📝 生成说明',
      'completed': '✨ 完成'
    };
    return stageMap[stage] || stage;
  };

  // 同步调用
  const planItinerarySync = async (): Promise<void> => {
    try {
      setLoading(true);
      setError('');
      setResult('');

      const request: PlanRequest = {
        user_input: userInput,
        session_id: sessionId
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/plan`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      });

      const data: ApiResponse = await response.json();

      if (data.success && data.data) {
        setResult(data.data.itinerary);
      } else {
        throw new Error(data.error || '规划失败');
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误';
      setError(errorMessage);
      console.error('行程规划失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 流式调用
  const planItineraryStream = async (): Promise<void> => {
    try {
      setLoading(true);
      setError('');
      setResult('');
      setProgress(0);
      setCurrentStage('');

      const request: PlanRequest = {
        user_input: userInput,
        session_id: sessionId
      };

      const response = await fetch(`${API_BASE_URL}/api/v1/plan/stream`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(request)
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body?.getReader();
      if (!reader) {
        throw new Error('无法读取响应流');
      }

      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        if (done) break;

        buffer += decoder.decode(value, { stream: true });
        const lines = buffer.split('\n');
        buffer = lines.pop() || '';

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data: StreamEvent = JSON.parse(line.slice(6));

              switch (data.type) {
                case 'start':
                  setCurrentStage(getStageName('analysis'));
                  break;
                case 'stage':
                  if (data.stage) {
                    setCurrentStage(getStageName(data.stage));
                  }
                  break;
                case 'progress':
                  if (data.message) {
                    setCurrentStage(data.message);
                  }
                  break;
                case 'complete':
                  if (data.data) {
                    setResult(data.data);
                    setCurrentStage(getStageName('completed'));
                    setProgress(100);
                  }
                  break;
                case 'error':
                  throw new Error(data.error || '未知错误');
              }
            } catch (parseError) {
              console.error('解析事件失败:', parseError);
            }
          }
        }
      }
    } catch (err) {
      const errorMessage = err instanceof Error ? err.message : '未知错误';
      setError(errorMessage);
      console.error('流式行程规划失败:', err);
    } finally {
      setLoading(false);
    }
  };

  // 处理提交
  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userInput.trim() || loading) return;

    if (useStream) {
      await planItineraryStream();
    } else {
      await planItinerarySync();
    }
  };

  // 重置结果
  const handleReset = () => {
    setResult('');
    setError('');
    setProgress(0);
    setCurrentStage('');
    setUserInput('');
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8 max-w-5xl">
        {/* 标题 */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">
            ✈️ 智能旅行规划助手
          </h1>
          <p className="text-gray-600">
            基于多Agent系统，为您定制专属旅行方案
          </p>
        </div>

        {/* 主卡片 */}
        <div className="bg-white rounded-2xl shadow-xl p-8 mb-8">
          {/* 输入表单 */}
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">
                告诉我您的旅行需求
              </label>
              <textarea
                value={userInput}
                onChange={(e) => setUserInput(e.target.value)}
                placeholder="例如：我想去东京旅游，计划3天，喜欢历史文化和美食，预算适中..."
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none transition-all"
                rows={5}
                disabled={loading}
              />
              <div className="mt-2 flex justify-between items-center">
                <span className="text-sm text-gray-500">
                  {userInput.length} / 2000 字符
                </span>
                <label className="flex items-center text-sm text-gray-600">
                  <input
                    type="checkbox"
                    checked={useStream}
                    onChange={(e) => setUseStream(e.target.checked)}
                    className="mr-2 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                  启用流式输出（实时显示进度）
                </label>
              </div>
            </div>

            {/* 提交按钮 */}
            <button
              type="submit"
              disabled={loading || !userInput.trim()}
              className="w-full bg-blue-600 text-white py-3 px-6 rounded-lg font-medium hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all transform hover:scale-[1.02] active:scale-[0.98]"
            >
              {loading ? 'AI正在规划您的行程...' : '开始规划'}
            </button>
          </form>

          {/* 加载状态 */}
          {loading && (
            <div className="mt-8 p-6 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-center justify-between mb-4">
                <div className="flex items-center space-x-3">
                  <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600" />
                  <span className="text-blue-900 font-medium">
                    {currentStage || '处理中...'}
                  </span>
                </div>
                <span className="text-blue-700 text-sm">
                  {progress}%
                </span>
              </div>
              {progress > 0 && (
                <div className="w-full bg-blue-200 rounded-full h-2">
                  <div
                    className="bg-blue-600 h-2 rounded-full transition-all duration-300"
                    style={{ width: `${progress}%` }}
                  />
                </div>
              )}
            </div>
          )}

          {/* 错误提示 */}
          {error && (
            <div className="mt-8 p-6 bg-red-50 rounded-lg border border-red-200 flex items-start space-x-3">
              <svg className="w-6 h-6 text-red-600 flex-shrink-0 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              <div className="flex-1">
                <h3 className="text-red-900 font-medium mb-1">出错了</h3>
                <p className="text-red-700 text-sm">{error}</p>
              </div>
              <button
                onClick={() => setError('')}
                className="text-red-500 hover:text-red-700"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          )}
        </div>

        {/* 结果展示 */}
        {result && (
          <div ref={resultRef} className="bg-white rounded-2xl shadow-xl overflow-hidden">
            {/* 结果头部 */}
            <div className="bg-gradient-to-r from-blue-600 to-indigo-600 px-8 py-6 flex justify-between items-center">
              <div>
                <h2 className="text-2xl font-bold text-white mb-1">
                  🎯 您的专属旅行方案
                </h2>
                <p className="text-blue-100 text-sm">
                  基于多Agent系统智能生成
                </p>
              </div>
              <button
                onClick={handleReset}
                className="bg-white/20 hover:bg-white/30 text-white px-4 py-2 rounded-lg transition-colors text-sm font-medium"
              >
                重新规划
              </button>
            </div>

            {/* 结果内容 */}
            <div className="p-8">
              <div className="prose prose-lg max-w-none prose-blue">
                <ReactMarkdown>{result}</ReactMarkdown>
              </div>
            </div>

            {/* 结果底部 */}
            <div className="bg-gray-50 px-8 py-4 border-t border-gray-200">
              <div className="flex justify-between items-center text-sm text-gray-600">
                <span>
                  会话ID: <code className="bg-gray-200 px-2 py-1 rounded">{sessionId}</code>
                </span>
                <span>
                  生成时间: {new Date().toLocaleString('zh-CN')}
                </span>
              </div>
            </div>
          </div>
        )}

        {/* 功能说明 */}
        <div className="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="text-3xl mb-3">🤖</div>
            <h3 className="font-bold text-gray-900 mb-2">多Agent协作</h3>
            <p className="text-gray-600 text-sm">
              行程规划 → 可行性校验 → 个性化输出，全流程AI驱动
            </p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="text-3xl mb-3">📚</div>
            <h3 className="font-bold text-gray-900 mb-2">知识库增强</h3>
            <p className="text-gray-600 text-sm">
              集成目的地知识库，提供官方权威信息和专业建议
            </p>
          </div>
          <div className="bg-white rounded-xl p-6 shadow-md">
            <div className="text-3xl mb-3">🔍</div>
            <h3 className="font-bold text-gray-900 mb-2">智能校验</h3>
            <p className="text-gray-600 text-sm">
              自动检查时间、距离、季节等因素，确保行程可行
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}
