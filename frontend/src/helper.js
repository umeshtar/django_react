
import axios from "axios";
import { api, env_api } from "../config";
import { useNavigate } from "react-router-dom";
import Cookies from "js-cookie";

export const authFetch = axios.create({ baseURL: env_api.API_URL });

export const postLogin = async (data) =>
  authFetch.post(env_api.API_URL, JSON.stringify(data), {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

const getAccessToken = () => {
  // const authUser = JSON.parse(sessionStorage.getItem("authUser"));
  const authUser = JSON.parse(Cookies.get("authUser"));
  return authUser ? authUser.access : null;
};

const setAccessToken = (token) => {
  // const authUser = JSON.parse(sessionStorage.getItem("authUser")) || {};
  const authUser = JSON.parse(Cookies.get("authUser")) || {};
  authUser.access = token;
  // sessionStorage.setItem("authUser", JSON.stringify(authUser));

  Cookies.set("authUser", JSON.stringify(authUser), {
    expires: 30,
  });
};

authFetch.interceptors.request.use(
  async (request) => {
    const accessToken = getAccessToken();
    if (accessToken) {
      request.headers["Authorization"] = `Bearer ${accessToken}`;
    }
    return request;
  },
  (error) => {
    return Promise.reject(error);
  }
);

authFetch.interceptors.response.use(
  (response) => {
    return response;
  },
  async (error) => {
    const originalRequest = error.config;

    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;

      // const refreshToken = JSON.parse(
      //   sessionStorage.getItem("authUser")
      // )?.refresh;
      const refreshToken = JSON.parse(Cookies.get("authUser"))?.refresh;

      if (
        error.response.config.url.includes("token_refresh") &&
        error.response.status === 401
      ) {
        sessionStorage.removeItem("authUser");
        Cookies.remove("authUser");
        window.location.href = "/login";
      }

      if (
        refreshToken &&
        !error.response.config.url.includes("token_refresh")
      ) {
        try {
          const response = await authFetch.post("/token_refresh/", {
            refresh: refreshToken,
          });

          const newAccessToken = response.data.access;
          setAccessToken(newAccessToken);

          originalRequest.headers["Authorization"] = `Bearer ${newAccessToken}`;
          return authFetch(originalRequest);
        } catch (refreshError) {
          console.log("Error refreshing token:", refreshError);
        }
      }
    }

    return Promise.reject(error);
  }
);

//Dashboard & Company
export const get_dashboard_data = async () => {
  return await authFetch.get(`/dashboard/`);
};

export const get_company_data = async () => authFetch.get(`/companies/`);

export const get_industry_type_data = async () =>
  authFetch.get(`/companies/industry_type/`);

export const add_company_data = async (data) =>
  authFetch.post(`/companies/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_company_data = async (data) =>
  authFetch.get(`/companies/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_company_data = async (data) =>
  authFetch.put(`/companies/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_company_data = async (data) =>
  authFetch.delete(`/companies/`, {
    data: data,
  });

export const set_company_as_favorite = async (data) =>
  authFetch.put(`/companies/set_favorite/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
//CompanyBranch
export const add_company_branch_data = async (data) =>
  authFetch.post(`/companies/company_branch/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_company_branch_data = async (data) =>
  authFetch.get(`/companies/company_branch/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const get_company_branch_data = async () => authFetch.get(`/companies/company_branch/`);


export const update_company_branch_data = async (data) =>
  authFetch.put(`/companies/company_branch/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_company_branch_data = async (data) =>
  authFetch.delete(`/companies/company_branch/`, {
    data: data,
  });
// Employee
export const get_employee_data = async () => authFetch.get(`/employees/`);

export const add_employee_data = async (data) =>
  authFetch.post(`/employees/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });
export const get_single_employee_data = async (data) =>
  authFetch.get(`/employees/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_employee_data = async (data) =>
  authFetch.put(`/employees/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_employee_data = async (data) =>
  authFetch.delete(`/employees/`, {
    data: data,
  });

// User
export const get_user_data = async () => authFetch.get(`/user_detail/`);

export const add_user_data = async (data) =>
  authFetch.post(`/user_detail/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_user_data = async (data) =>
  authFetch.get(`/user_detail/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_user_data = async (data) =>
  authFetch.put(`/user_detail/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_user_data = async (data) =>
  authFetch.delete(`/user_detail/`, {
    data: data,
  });

// User  Profile
export const get_user_data_profile = async () =>
  authFetch.get(`/user_profile/`);

export const add_user_data_profile = async (data) =>
  authFetch.post(`/user_profile/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_user_data_profile = async (data) =>
  authFetch.get(`/user_profile/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_user_data_profile = async (data) =>
  authFetch.put(`/user_profile/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_user_data_profile = async (data) =>
  authFetch.delete(`/user_profile/`, {
    data: data,
  });

// Department
export const get_department_data = async () =>
  authFetch.get(`/employees/department/`);

export const add_department_data = async (data) =>
  authFetch.post(`/employees/department/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_department_data = async (data) =>
  authFetch.get(`/employees/department/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_department_data = async (data) =>
  authFetch.put(`/employees/department/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_department_data = async (data) =>
  authFetch.delete(`/employees/department/`, {
    data: data,
  });

// Designation
export const get_designation_data = async () =>
  authFetch.get(`/employees/designation/`);

export const add_designation_data = async (data) =>
  authFetch.post(`/employees/designation/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_designation_data = async (data) =>
  authFetch.get(`/employees/designation/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_designation_data = async (data) =>
  authFetch.put(`/employees/designation/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_designation_data = async (data) =>
  authFetch.delete(`/employees/designation/`, {
    data: data,
  });

// Industry
export const get_industry_data = async () =>
  authFetch.get(`/companies/industry_type/`);

export const add_industry_data = async (data) =>
  authFetch.post(`/companies/industry_type/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_industry_data = async (data) =>
  authFetch.get(`/companies/industry_type/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_industry_data = async (data) =>
  authFetch.put(`/companies/industry_type/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_industry_data = async (data) =>
  authFetch.delete(`/companies/industry_type/`, {
    data: data,
  });


export const delete_single_owner_data = async (data) =>
  authFetch.delete(`/companies/owner/`, {
    data: data,
  });


// Letter_type
export const get_letter_type_data = async () =>
  authFetch.get(`/employees/letter_type/`);

export const add_letter_type_data = async (data) =>
  authFetch.post(`/employees/letter_type/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_letter_type_data = async (data) =>
  authFetch.get(`/employees/letter_type/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_letter_type_data = async (data) =>
  authFetch.put(`/employees/letter_type/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_letter_type_data = async (data) =>
  authFetch.delete(`/employees/letter_type/`, {
    data: data,
  });

// Bank_master
export const get_bank_master_data = async () =>
  authFetch.get(`/employees/bank-master/`);

export const add_bank_master_data = async (data) =>
  authFetch.post(`/employees/bank-master/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_bank_master_data = async (data) =>
  authFetch.get(`/employees/bank-master/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_bank_master_data = async (data) =>
  authFetch.put(`/employees/bank-master/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_bank_master_data = async (data) =>
  authFetch.delete(`/employees/bank-master/`, {
    data: data,
  });

// Employee Bank
export const get_employee_bank_data = async () =>
  authFetch.get(`/employees/bank/`);

export const add_employee_bank_data = async (data) =>
  authFetch.post(`/employees/bank/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_employee_bank_data = async (data) =>
  authFetch.get(`/employees/bank/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_employee_bank_data = async (data) =>
  authFetch.put(`/employees/bank/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_employee_bank_data = async (data) =>
  authFetch.delete(`/employees/bank/`, {
    data: data,
  });

// Employee Experience
export const get_employee_experience_data = async () =>
  authFetch.get(`/employees/employee_experience/`);

export const add_employee_experience_data = async (data) =>
  authFetch.post(`/employees/employee_experience/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_employee_experience_data = async (data) =>
  authFetch.get(`/employees/employee_experience/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_employee_experience_data = async (data) =>
  authFetch.put(`/employees/employee_experience/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_employee_experience_data = async (data) =>
  authFetch.delete(`/employees/employee_experience/`, {
    data: data,
  });

// Employee Note
export const get_employee_note_data = async () =>
  authFetch.get(`/employees/employee_note/`);

export const add_employee_note_data = async (data) =>
  authFetch.post(`/employees/employee_note/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_employee_note_data = async (data) =>
  authFetch.get(`/employees/employee_note/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_employee_note_data = async (data) =>
  authFetch.put(`/employees/employee_note/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_employee_note_data = async (data) =>
  authFetch.delete(`/employees/employee_note/`, {
    data: data,
  });

// Employee Salary
export const get_employee_salary_data = async () =>
  authFetch.get(`/employees/salary/`);

export const add_employee_salary_data = async (data) =>
  authFetch.post(`/employees/salary/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_single_employee_salary_data = async (data) =>
  authFetch.get(`/employees/salary/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_employee_salary_data = async (data) =>
  authFetch.put(`/employees/salary/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_employee_salary_data = async (data) =>
  authFetch.delete(`/employees/salary/`, {
    data: data,
  });

// Employee Payment Mode
export const get_employee_payment_mode_data = async () =>
  authFetch.get(`/employees/payment_mode/`);

// Country Code
export const get_country_code_data = async () =>
  authFetch.get(`/companies/country_code/`);

//Global Search
export const get_globalSearch_data = async ({ searchfrom, searchinput }) =>
  authFetch.get(`/Global_search/?search=${searchfrom}&query=${searchinput}`);

// Setting Congiguration
export const get_system_configuration = async () =>
  authFetch.get(`/configuration/`);

export const add_system_configuration = async (data) =>
  authFetch.post(`/configuration/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

// Organization Tree
export const get_system_organization_tree = async (data) =>
  authFetch.get(`/employees/organization_tree/`, data);

// Social Media Master table data
export const get_social_media_data = async () =>
  authFetch.get(`/utilities/social_media/`);

export const add_social_media_data = async (data) =>
  authFetch.post(`/utilities/social_media/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const excelFiles = (data) =>
  authFetch.post(`/companies/import_employee/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const get_social_media_master_data = async (data) =>
  authFetch.get(`/utilities/social_media/`, {
    headers: {
      "Content-Type": "application/json",
    },
    params: data,
  });

export const update_social_media_data = async (data) =>
  authFetch.put(`/utilities/social_media/`, data, {
    headers: {
      "Content-Type": "multipart/form-data",
    },
  });

export const delete_single_social_media_data = async (data) =>
  authFetch.delete(`/utilities/social_media/`, {
    data: data,
  });

const getLoggedinUser = () => {
  // const user = sessionStorage.getItem("authUser");
  const user = Cookies.get("authUser");
  if (!user) {
    return null;
  } else {
    return JSON.parse(user);
  }
};

// export { APIClient, setAuthorization, getLoggedinUser };
export { getLoggedinUser };
