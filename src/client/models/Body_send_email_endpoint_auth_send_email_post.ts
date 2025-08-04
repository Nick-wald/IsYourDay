

export type Body_send_email_endpoint_auth_send_email_post = {
	/**
	 * 接收者用户ID列表
	 */
	receiver: Array<string>;
	/**
	 * 邮件主题
	 */
	subject?: string;
	/**
	 * 邮件内容（支持HTML）
	 */
	content?: string;
	files?: Array<Blob> | null;
	files_in_store?: Array<string> | null;
	/**
	 * 是否存储上传的文件到服务器
	 */
	store_upload_files?: boolean;
};

