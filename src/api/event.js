// import { service } from "../utils/request";
import { service } from '../utils/request';
export const getUserEvent = (user_id) => {
    return service.get(`/isyourday/user/${user_id}/events`);
};
export const addEventOrMsg = (user_id, data) => {
    return service.post(`/isyourday/user/${user_id}/events`, data);
};
export const updateEventOrMsg = (user_id, event_id, data) => {
    return service.patch(`/isyourday/user/${user_id}/event/${event_id}`, data);
};
export const delEventOrMsg = (user_id, data) => {
    // const obj = JSON.stringify(data)
    return service.delete(`/isyourday/user/${user_id}/events/batch`, { data: data });
};
export const sendemail = (email_type, formData) => {
    return service.post(`/auth/send-email/${email_type}`, formData, {
        headers: {
            'Content-Type': 'multipart/form-data' // 关键设置
        }
    });
};
export const getEmailHistory = (search_type, data) => {
    return service.get(`/auth/send-email/history/${search_type}`, { params: data });
};
export const updateEmailHistory = (history_id, data) => {
    return service.patch(`/auth/send-email/history?history_id=${history_id}`, data);
};
export const sendPendingEmail = (history_id) => {
    return service.get(`/auth/send-email/pending/${history_id}`);
};
//# sourceMappingURL=event.js.map