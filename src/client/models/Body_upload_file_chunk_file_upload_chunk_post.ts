

export type Body_upload_file_chunk_file_upload_chunk_post = {
	file: Blob;
	/**
	 * 分片索引（从0开始）
	 */
	chunk_index: number;
	/**
	 * 总分片数
	 */
	total_chunks: number;
	/**
	 * 文件唯一标识符
	 */
	file_id: string;
	/**
	 * 原始文件名
	 */
	original_filename: string;
	/**
	 * 文件总大小
	 */
	total_size: number;
	/**
	 * 是否公开文件
	 */
	is_public?: boolean;
};

