export const CHANGE_EMAIL_DIALOG_STATES = {
  NONE: 0, // Dialog非表示
  SEND_VERIFICATION_EMAIL: 1, // 認証メール送信Dialog
  ENTER_VERIFICATION_CODE: 2, // 認証コード入力Dialog
  CHANGE_EMAIL_FORM: 3, // メールアドレス変更Dialog
};

export const UPDATE_PASSWORD_DIALOG_STATES = {
  NONE: 0, // Dialog非表示
  UPDATE_PASSWORD: 1, // パスワード入力Dialog
};
