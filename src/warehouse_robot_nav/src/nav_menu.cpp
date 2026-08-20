#include <ament_index_cpp/get_package_share_directory.hpp>
#include <geometry_msgs/msg/pose_stamped.hpp>
#include <nav2_msgs/action/navigate_to_pose.hpp>
#include <rclcpp/rclcpp.hpp>
#include <rclcpp_action/rclcpp_action.hpp>

#include <chrono>
#include <cmath>
#include <fstream>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <thread>
#include <vector>

using NavigateToPose = nav2_msgs::action::NavigateToPose;
using GoalHandleNav = rclcpp_action::ClientGoalHandle<NavigateToPose>;

struct Location {
  std::string id;
  std::string name;
  double x;
  double y;
  double yaw;
};

std::vector<std::string> split_csv_line(const std::string & line)
{
  std::vector<std::string> fields;
  std::stringstream stream(line);
  std::string field;
  while (std::getline(stream, field, ',')) {
    fields.push_back(field);
  }
  return fields;
}

std::vector<Location> load_locations()
{
  const auto share = ament_index_cpp::get_package_share_directory("warehouse_robot_nav");
  const auto path = share + "/config/locations.csv";
  std::ifstream input(path);
  if (!input) {
    throw std::runtime_error("Could not open canonical locations file: " + path);
  }

  std::vector<Location> locations;
  std::string line;
  std::getline(input, line);  // Header.
  while (std::getline(input, line)) {
    if (line.empty()) {
      continue;
    }
    const auto fields = split_csv_line(line);
    if (fields.size() != 7) {
      throw std::runtime_error("Invalid row in canonical locations file");
    }
    locations.push_back(
      Location{fields[0], fields[1], std::stod(fields[2]), std::stod(fields[3]),
        std::stod(fields[4])});
  }
  if (locations.empty()) {
    throw std::runtime_error("Canonical locations file contains no destinations");
  }
  return locations;
}

class NavMenuNode : public rclcpp::Node
{
public:
  NavMenuNode()
  : Node("nav_menu_node"), goal_done_(true)
  {
    client_ = rclcpp_action::create_client<NavigateToPose>(this, "navigate_to_pose");
    RCLCPP_INFO(get_logger(), "Nav menu node started");
  }

  bool send_goal(const Location & location)
  {
    goal_done_ = false;
    if (!client_->wait_for_action_server(std::chrono::seconds(5))) {
      RCLCPP_ERROR(get_logger(), "Nav2 action server is not available");
      goal_done_ = true;
      return false;
    }

    auto goal = NavigateToPose::Goal();
    goal.pose.header.frame_id = "map";
    goal.pose.header.stamp = get_clock()->now();
    goal.pose.pose.position.x = location.x;
    goal.pose.pose.position.y = location.y;
    goal.pose.pose.orientation.z = std::sin(location.yaw / 2.0);
    goal.pose.pose.orientation.w = std::cos(location.yaw / 2.0);

    auto options = rclcpp_action::Client<NavigateToPose>::SendGoalOptions();
    options.goal_response_callback = [this, name = location.name](
      const GoalHandleNav::SharedPtr & handle)
      {
        if (!handle) {
          RCLCPP_ERROR(get_logger(), "Nav2 rejected the goal for %s", name.c_str());
          goal_done_ = true;
          return;
        }
        RCLCPP_INFO(get_logger(), "Nav2 accepted the goal for %s", name.c_str());
      };
    options.result_callback = [this, name = location.name](
      const GoalHandleNav::WrappedResult & result)
      {
        switch (result.code) {
          case rclcpp_action::ResultCode::SUCCEEDED:
            RCLCPP_INFO(get_logger(), "Nav2 reached %s successfully", name.c_str());
            break;
          case rclcpp_action::ResultCode::ABORTED:
            RCLCPP_ERROR(get_logger(), "Navigation to %s was aborted", name.c_str());
            break;
          case rclcpp_action::ResultCode::CANCELED:
            RCLCPP_WARN(get_logger(), "Navigation to %s was canceled", name.c_str());
            break;
          default:
            RCLCPP_ERROR(get_logger(), "Navigation to %s returned an unknown result", name.c_str());
            break;
        }
        goal_done_ = true;
      };

    client_->async_send_goal(goal, options);
    return true;
  }

  bool goal_done() const {return goal_done_;}

private:
  rclcpp_action::Client<NavigateToPose>::SharedPtr client_;
  bool goal_done_;
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  try {
    const auto locations = load_locations();
    auto node = std::make_shared<NavMenuNode>();

    std::cout << "\nWAREHOUSE ROBOT NAVIGATION MENU\n";
    while (rclcpp::ok()) {
      std::cout << "\nSelect a destination:\n";
      for (std::size_t index = 0; index < locations.size(); ++index) {
        std::cout << "  " << index + 1 << ". " << locations[index].name << '\n';
      }
      std::cout << "  0. Exit\n\nEnter number: ";

      int choice = -1;
      if (!(std::cin >> choice)) {
        std::cin.clear();
        std::cin.ignore(std::numeric_limits<std::streamsize>::max(), '\n');
        std::cout << "Invalid input; enter a number.\n";
        continue;
      }
      if (choice == 0) {
        break;
      }
      if (choice < 1 || choice > static_cast<int>(locations.size())) {
        std::cout << "Invalid destination number.\n";
        continue;
      }

      const auto & location = locations[static_cast<std::size_t>(choice - 1)];
      std::cout << "Navigating to " << location.name << " at (" << location.x << ", "
                << location.y << ")\n";
      if (!node->send_goal(location)) {
        continue;
      }
      while (rclcpp::ok() && !node->goal_done()) {
        rclcpp::spin_some(node);
        std::this_thread::sleep_for(std::chrono::milliseconds(100));
      }
    }
  } catch (const std::exception & error) {
    std::cerr << "Navigation menu failed: " << error.what() << '\n';
    rclcpp::shutdown();
    return 1;
  }
  rclcpp::shutdown();
  return 0;
}
