#pragma once

#include <opencv2/opencv.hpp>
#include <vector>
#include <map>

#include "tools/FileSystem.hpp"
#include "tools/StringExtend.hpp"

#define UNKNOWN_FLOW_THRESH 1e9

using namespace cv;
using namespace std;

class DynamicBackgroundOpticalFlow {
private:
	static constexpr int N = 1500;
	int flag[N][N];

	Mat prevgray, gray, flow, cflow, frame, pre_frame, img_scale, img_temp, mask = Mat(Size(1, 300), CV_8UC1);;
	Size dsize;
	vector<Point2f> prepoint, nextpoint;
	vector<Point2f> F_prepoint, F_nextpoint;
	vector<uchar> state;
	vector<float> err;
	double dis[N];
	int cal = 0;
	int width = 100, height = 100;
	int rec_width = 40;
	int Harris_num = 0;
	int flag2 = 0;

	/// 算法参数
	FileSystem::Loader loader;

	double vehicle_speed;
	double limit_of_check;
	double scale; //设置缩放倍数
	int margin; //帧间隔
	double limit_dis_epi; //距离极线的距离

	// 参数
	map<string, string> videos;
	string output;

public:
	DynamicBackgroundOpticalFlow();
	bool ROI_mod(int x1, int y1);
	void ready();
	void optical_flow_check();
	bool stable_judge();
  void run(string path);
};