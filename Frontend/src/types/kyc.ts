export type ImageAsset = {
  uri: string;
  name: string;
  type: string;
};

export type KycUploadPayload = {
  nationalId: string;
  residentialAddress: string;
  idFront: ImageAsset;
  idBack: ImageAsset;
  selfie: ImageAsset;
};
